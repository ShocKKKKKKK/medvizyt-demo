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

if (mb_strlen($name) < 2 || strlen(preg_replace('/\D/', '', $phone)) < 10 || $service === '') {
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

$lines = [
	'<b>Нова заявка з сайту</b> · ' . $lang,
	'',
	'<b>ПІБ:</b> ' . $e($name),
	'<b>Телефон:</b> ' . $e($phone),
	'<b>Документ:</b> ' . $e($service),
];
if ($comment !== '') {
	$lines[] = '<b>Додатково:</b> ' . $e($comment);
}
if ($page !== '') {
	$lines[] = '';
	$lines[] = '<b>Сторінка:</b> ' . $e($page);
}
$lines[] = '<b>Час:</b> ' . date('d.m.Y H:i');

$payload = http_build_query([
	'chat_id' => $chatId,
	'text' => implode("\n", $lines),
	'parse_mode' => 'HTML',
	'disable_web_page_preview' => 'true',
]);

$ch = curl_init('https://api.telegram.org/bot' . $token . '/sendMessage');
curl_setopt_array($ch, [
	CURLOPT_POST => true,
	CURLOPT_POSTFIELDS => $payload,
	CURLOPT_RETURNTRANSFER => true,
	CURLOPT_TIMEOUT => 10,
]);
$response = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

$result = json_decode((string) $response, true);
if ($status !== 200 || empty($result['ok'])) {
	reply(502, ['ok' => false, 'error' => 'telegram']);
}

reply(200, ['ok' => true]);
