<?php
/**
 * Приймає заявку з форми сайту і пересилає її в Telegram.
 *
 * Налаштування бота — у файлі tg-config.php поруч (шаблон: tg-config.example.php).
 * Токен лежить на сервері і в браузер не потрапляє.
 * Відповідь — JSON: {"ok": true} або {"ok": false, "error": "..."}.
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function reply(int $code, array $data): void
{
	http_response_code($code);
	echo json_encode($data, JSON_UNESCAPED_UNICODE);
	exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
	reply(405, ['ok' => false, 'error' => 'method']);
}

$configFile = __DIR__ . '/tg-config.php';
if (!is_file($configFile)) {
	reply(500, ['ok' => false, 'error' => 'config']);
}
$config = require $configFile;
$token = trim($config['bot_token'] ?? '');
$chatId = trim((string) ($config['chat_id'] ?? ''));
if ($token === '' || $chatId === '') {
	reply(500, ['ok' => false, 'error' => 'config']);
}

// Пастка для ботів: це поле людина не бачить і не заповнює
if (!empty($_POST['hp_note'])) {
	reply(200, ['ok' => true]);
}

function field(string $name, int $max): string
{
	$value = trim((string) ($_POST[$name] ?? ''));
	$value = preg_replace('/\s+/u', ' ', $value);
	return mb_substr($value, 0, $max);
}

$name = field('name', 120);
$phone = field('phone', 40);
$service = field('service', 160);
$comment = trim(mb_substr((string) ($_POST['comment'] ?? ''), 0, 1000));
$page = field('page', 300);
$lang = field('lang', 5) === 'ru' ? 'RU' : 'UA';

$details = json_decode((string) ($_POST['details'] ?? ''), true);
if (!is_array($details)) {
	$details = [];
}

$upload = null;
foreach ($_FILES as $file) {
	$error = (int) ($file['error'] ?? UPLOAD_ERR_NO_FILE);
	if ($error === UPLOAD_ERR_NO_FILE) {
		continue;
	}
	if ($error !== UPLOAD_ERR_OK || !is_uploaded_file((string) ($file['tmp_name'] ?? ''))) {
		reply(422, ['ok' => false, 'error' => 'upload']);
	}
	if ((int) ($file['size'] ?? 0) > 8 * 1024 * 1024) {
		reply(413, ['ok' => false, 'error' => 'file_size']);
	}
	$mime = (new finfo(FILEINFO_MIME_TYPE))->file((string) $file['tmp_name']);
	$allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif', 'application/pdf'];
	if (!in_array($mime, $allowed, true)) {
		reply(415, ['ok' => false, 'error' => 'file_type']);
	}
	$upload = [
		'tmp_name' => (string) $file['tmp_name'],
		'name' => mb_substr(basename((string) ($file['name'] ?? 'photo')), 0, 120),
		'mime' => $mime,
	];
	break;
}

if (strlen(preg_replace('/\D/', '', $phone)) < 10 || (empty($details) && $service === '')) {
	reply(422, ['ok' => false, 'error' => 'fields']);
}

// Не частіше однієї заявки на 20 секунд з однієї IP-адреси
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$lockFile = sys_get_temp_dir() . '/ma-form-' . md5($ip);
if (is_file($lockFile) && time() - filemtime($lockFile) < 20) {
	reply(429, ['ok' => false, 'error' => 'often']);
}
@touch($lockFile);

$e = static fn(string $s): string => htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

$lines = ['<b>Нова заявка з сайту</b> · ' . $lang, ''];
if (!empty($details)) {
	foreach ($details as $d) {
		$label = $e((string) ($d['label'] ?? ''));
		$value = $e((string) ($d['value'] ?? ''));
		if ($label !== '' && $value !== '') {
			$lines[] = '<b>' . $label . ':</b> ' . $value;
		}
	}
} else {
	if ($name !== '') {
		$lines[] = '<b>ПІБ:</b> ' . $e($name);
	}
	$lines[] = '<b>Телефон:</b> ' . $e($phone);
	$lines[] = '<b>Документ:</b> ' . $e($service);
	if ($comment !== '') {
		$lines[] = '<b>Додатково:</b> ' . $e($comment);
	}
}
if ($page !== '') {
	$lines[] = '';
	$lines[] = '<b>Сторінка:</b> ' . $e($page);
}
$lines[] = '<b>Час:</b> ' . date('d.m.Y H:i');

$text = implode("\n", $lines);
if (mb_strlen($text) > 3800) {
	$text = mb_substr($text, 0, 3800) . '…';
}

function telegramRequest(string $token, string $method, array $payload): bool
{
	$ch = curl_init('https://api.telegram.org/bot' . $token . '/' . $method);
	curl_setopt_array($ch, [
		CURLOPT_POST => true,
		CURLOPT_POSTFIELDS => $payload,
		CURLOPT_RETURNTRANSFER => true,
		CURLOPT_TIMEOUT => 15,
	]);
	$response = curl_exec($ch);
	$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
	curl_close($ch);
	$result = json_decode((string) $response, true);
	return $status === 200 && !empty($result['ok']);
}

// Сначала отправляем вложение: если Telegram его не принял, заявка не считается завершённой.
if ($upload !== null) {
	$captionParts = ['Вкладення до нової заявки'];
	if ($name !== '') {
		$captionParts[] = $name;
	}
	if ($phone !== '') {
		$captionParts[] = $phone;
	}
	$fileSent = telegramRequest($token, 'sendDocument', [
		'chat_id' => $chatId,
		'document' => new CURLFile($upload['tmp_name'], $upload['mime'], $upload['name']),
		'caption' => implode(' · ', $captionParts),
	]);
	if (!$fileSent) {
		reply(502, ['ok' => false, 'error' => 'telegram_file']);
	}
}

$messageSent = telegramRequest($token, 'sendMessage', [
	'chat_id' => $chatId,
	'text' => $text,
	'parse_mode' => 'HTML',
	'disable_web_page_preview' => 'true',
]);
if (!$messageSent) {
	reply(502, ['ok' => false, 'error' => 'telegram']);
}

reply(200, ['ok' => true]);
