<?php

declare(strict_types=1);

use PHPMailer\PHPMailer\PHPMailer;

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

/** Отправляет единообразный JSON-ответ и завершает обработку. */
function reply(int $status, array $payload): void
{
	http_response_code($status);
	echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
	exit;
}

/** Возвращает очищенную строку из POST с ограничением длины. */
function postString(string $name, int $limit = 500): string
{
	$value = trim((string) ($_POST[$name] ?? ''));
	$value = preg_replace('/\s+/u', ' ', $value) ?? '';
	return function_exists('mb_substr') ? mb_substr($value, 0, $limit) : substr($value, 0, $limit);
}

/** Экранирует пользовательский текст для HTML-письма. */
function escapeHtml(string $value): string
{
	return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
	reply(405, ['ok' => false, 'error' => 'method']);
}

// Honeypot: человек это поле не видит, а бот обычно заполняет.
if (postString('hp_note', 100) !== '') {
	reply(200, ['ok' => true]);
}

// Заявка не может быть отправлена быстрее трёх секунд после загрузки формы.
// form_elapsed считает браузер монотонным таймером, поэтому сбитые часы у посетителя не мешают.
// form_started_at оставлен для старых закэшированных версий main.js.
$elapsedField = filter_var($_POST['form_elapsed'] ?? null, FILTER_VALIDATE_INT);
if ($elapsedField !== false && $elapsedField !== null) {
	$elapsed = (int) $elapsedField;
} else {
	$startedAt = filter_var($_POST['form_started_at'] ?? null, FILTER_VALIDATE_INT);
	$elapsed = $startedAt ? time() - (int) $startedAt : -1;
	// Часы посетителя могут спешить: отрицательную разницу не считаем спамом.
	if ($startedAt && $elapsed < 0) {
		$elapsed = 3;
	}
}
if ($elapsed < 3 || $elapsed > 604800) {
	reply(422, ['ok' => false, 'error' => 'spam_time']);
}

$configFile = __DIR__ . '/config.php';
if (!is_file($configFile)) {
	reply(500, ['ok' => false, 'error' => 'config']);
}

$config = require $configFile;
if (!is_array($config)) {
	reply(500, ['ok' => false, 'error' => 'config']);
}

$requiredConfig = ['host', 'port', 'username', 'password', 'from_email', 'from_name'];
foreach ($requiredConfig as $key) {
	$value = trim((string) ($config[$key] ?? ''));
	if ($value === '' || strpos($value, 'ВПИШИТЕ_') !== false) {
		reply(500, ['ok' => false, 'error' => 'config']);
	}
}
if (!array_key_exists('encryption', $config)) {
	reply(500, ['ok' => false, 'error' => 'config']);
}

require_once __DIR__ . '/vendor/phpmailer/src/Exception.php';
require_once __DIR__ . '/vendor/phpmailer/src/PHPMailer.php';
require_once __DIR__ . '/vendor/phpmailer/src/SMTP.php';

$name = postString('name', 120);
$phone = postString('phone', 40);
$service = postString('service', 180);
$comment = postString('comment', 1500);
$page = postString('page', 500);
$pageTitle = postString('page_title', 200);
$formTitle = postString('form_title', 160);
$formKind = postString('form_kind', 20) === 'order' ? 'order' : 'simple';
$consent = isset($_POST['consent']) && in_array(strtolower((string) $_POST['consent']), ['1', 'on', 'true', 'yes'], true);

$details = json_decode((string) ($_POST['details'] ?? ''), true);
if (!is_array($details)) {
	$details = [];
}
$cleanDetails = [];
foreach ($details as $detail) {
	if (!is_array($detail)) {
		continue;
	}
	$label = trim((string) ($detail['label'] ?? ''));
	$value = trim((string) ($detail['value'] ?? ''));
	if ($label === '' || $value === '') {
		continue;
	}
	$cleanDetails[] = [
		'label' => function_exists('mb_substr') ? mb_substr($label, 0, 180) : substr($label, 0, 180),
		'value' => function_exists('mb_substr') ? mb_substr($value, 0, 1500) : substr($value, 0, 1500),
	];
}

$requiredFields = json_decode((string) ($_POST['required_fields'] ?? ''), true);
if (!is_array($requiredFields)) {
	$requiredFields = [];
}

$phoneDigits = preg_replace('/\D/', '', $phone) ?? '';
if (!$consent || strlen($phoneDigits) < 10) {
	reply(422, ['ok' => false, 'error' => 'fields']);
}
if ($formKind === 'simple' && (strlen($name) < 2 || $service === '')) {
	reply(422, ['ok' => false, 'error' => 'fields']);
}
if ($formKind === 'order') {
	if ($cleanDetails === [] || $requiredFields === []) {
		reply(422, ['ok' => false, 'error' => 'fields']);
	}
	foreach ($requiredFields as $fieldName) {
		$fieldName = (string) $fieldName;
		if (!preg_match('/^f\d+$/', $fieldName)) {
			reply(422, ['ok' => false, 'error' => 'fields']);
		}
		$value = $_POST[$fieldName] ?? null;
		$file = $_FILES[$fieldName] ?? null;
		$hasValue = is_array($value)
			? count(array_filter($value, static fn($item): bool => trim((string) $item) !== '')) > 0
			: trim((string) $value) !== '';
		$hasFile = is_array($file) && (int) ($file['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_OK;
		if (!$hasValue && !$hasFile) {
			reply(422, ['ok' => false, 'error' => 'fields']);
		}
	}
}

// Ограничение повторных заявок с одного IP-адреса.
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? 'unknown');
$lockFile = sys_get_temp_dir() . '/med-assistant-form-' . hash('sha256', $ip);
if (is_file($lockFile) && time() - (int) filemtime($lockFile) < 15) {
	reply(429, ['ok' => false, 'error' => 'often']);
}

$attachments = [];
foreach ($_FILES as $file) {
	$error = (int) ($file['error'] ?? UPLOAD_ERR_NO_FILE);
	if ($error === UPLOAD_ERR_NO_FILE) {
		continue;
	}
	$tmpName = (string) ($file['tmp_name'] ?? '');
	if ($error !== UPLOAD_ERR_OK || !is_uploaded_file($tmpName)) {
		reply(422, ['ok' => false, 'error' => 'upload']);
	}
	if ((int) ($file['size'] ?? 0) > 8 * 1024 * 1024) {
		reply(413, ['ok' => false, 'error' => 'file_size']);
	}
	$mime = (new finfo(FILEINFO_MIME_TYPE))->file($tmpName);
	$allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif', 'application/pdf'];
	if (!in_array($mime, $allowedTypes, true)) {
		reply(415, ['ok' => false, 'error' => 'file_type']);
	}
	$attachments[] = [
		'path' => $tmpName,
		'name' => basename((string) ($file['name'] ?? 'attachment')),
	];
}

date_default_timezone_set('Europe/Kyiv');
$sentAt = date('d.m.Y H:i:s');
$subjectLabel = $formTitle !== '' ? $formTitle : ($pageTitle !== '' ? $pageTitle : 'форма сайту');
$subjectLabel = preg_replace('/[\r\n]+/', ' ', $subjectLabel) ?? 'форма сайту';
$subject = 'Нова заявка з сайту — ' . $subjectLabel;

$rows = [];
if ($cleanDetails !== []) {
	foreach ($cleanDetails as $detail) {
		$rows[] = '<tr><th align="left" style="padding:8px 12px;border-bottom:1px solid #dce9e7;">'
			. escapeHtml($detail['label']) . '</th><td style="padding:8px 12px;border-bottom:1px solid #dce9e7;">'
			. nl2br(escapeHtml($detail['value'])) . '</td></tr>';
	}
} else {
	$baseFields = [
		'ПІБ' => $name,
		'Телефон' => $phone,
		'Документ' => $service,
		'Додаткова інформація' => $comment,
	];
	foreach ($baseFields as $label => $value) {
		if ($value === '') {
			continue;
		}
		$rows[] = '<tr><th align="left" style="padding:8px 12px;border-bottom:1px solid #dce9e7;">'
			. escapeHtml($label) . '</th><td style="padding:8px 12px;border-bottom:1px solid #dce9e7;">'
			. nl2br(escapeHtml($value)) . '</td></tr>';
	}
}

$metaRows = [
	'Згода на обробку даних' => 'Так',
	'Назва форми' => $subjectLabel,
	'Сторінка' => $pageTitle,
	'Посилання' => $page,
	'Дата і час' => $sentAt,
];
foreach ($metaRows as $label => $value) {
	$rows[] = '<tr><th align="left" style="padding:8px 12px;border-bottom:1px solid #dce9e7;">'
		. escapeHtml($label) . '</th><td style="padding:8px 12px;border-bottom:1px solid #dce9e7;">'
		. escapeHtml($value !== '' ? $value : '—') . '</td></tr>';
}

$body = '<div style="font-family:Arial,sans-serif;color:#0b2b30;">'
	. '<h1 style="font-size:24px;">Нова заявка з сайту</h1>'
	. '<table cellpadding="0" cellspacing="0" style="width:100%;max-width:760px;border:1px solid #dce9e7;border-radius:12px;border-collapse:separate;overflow:hidden;">'
	. implode('', $rows)
	. '</table></div>';

$plain = "Нова заявка з сайту\n";
foreach ($cleanDetails as $detail) {
	$plain .= $detail['label'] . ': ' . $detail['value'] . "\n";
}
if ($cleanDetails === []) {
	$plain .= "ПІБ: {$name}\nТелефон: {$phone}\nДокумент: {$service}\n";
	if ($comment !== '') {
		$plain .= "Додаткова інформація: {$comment}\n";
	}
}
$plain .= "Згода на обробку даних: Так\nСторінка: {$pageTitle}\nПосилання: {$page}\nДата і час: {$sentAt}";

try {
	$mail = new PHPMailer(true);
	$mail->CharSet = PHPMailer::CHARSET_UTF8;
	$mail->isSMTP();
	$mail->Host = trim((string) $config['host']);
	$mail->Port = (int) $config['port'];
	$mail->SMTPAuth = true;
	$mail->Username = trim((string) $config['username']);
	$mail->Password = (string) $config['password'];

	$encryption = strtolower(trim((string) $config['encryption']));
	if (in_array($encryption, ['ssl', 'smtps'], true)) {
		$mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;
	} elseif (in_array($encryption, ['tls', 'starttls'], true)) {
		$mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
	} else {
		$mail->SMTPSecure = '';
		$mail->SMTPAutoTLS = false;
	}

	$fromEmail = trim((string) $config['from_email']);
	// Домен отправителя в EHLO и Message-ID вместо технического имени VPS — меньше шансов попасть в спам.
	$fromDomain = substr((string) strrchr($fromEmail, '@'), 1);
	if ($fromDomain !== '') {
		$mail->Hostname = $fromDomain;
		$mail->Helo = $fromDomain;
	}
	$mail->setFrom($fromEmail, trim((string) $config['from_name']));
	// Получатели берутся из config.php; без настройки — адреса заказчика.
	$recipients = $config['to'] ?? ['verbadianaka@gmail.com', 'mail@zayavkionline.com'];
	foreach ((array) $recipients as $recipient) {
		$recipient = trim((string) $recipient);
		if ($recipient !== '') {
			$mail->addAddress($recipient);
		}
	}
	$mail->isHTML(true);
	$mail->Subject = $subject;
	$mail->Body = $body;
	$mail->AltBody = $plain;

	foreach ($attachments as $attachment) {
		$mail->addAttachment($attachment['path'], $attachment['name']);
	}

	$mail->send();
	@touch($lockFile);
	reply(200, ['ok' => true]);
} catch (Throwable $error) {
	error_log('Med-assistant SMTP: ' . $error->getMessage());
	reply(502, ['ok' => false, 'error' => 'mail']);
}
