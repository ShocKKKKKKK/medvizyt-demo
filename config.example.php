<?php

/**
 * Пример SMTP-настроек.
 * Скопируйте файл как config.php и замените значения на данные клиента.
 */
return [
	'host' => 'ВПИШИТЕ_SMTP_ХОСТ',
	'port' => 587,
	'encryption' => 'tls',
	'username' => 'ВПИШИТЕ_SMTP_ЛОГИН',
	'password' => 'ВПИШИТЕ_SMTP_ПАРОЛЬ',
	'from_email' => 'ВПИШИТЕ_EMAIL_ОТПРАВИТЕЛЯ',
	'from_name' => 'Med-assistant',
	// Кому отправлять заявки.
	'to' => ['verbadianaka@gmail.com', 'mail@zayavkionline.com'],
];
