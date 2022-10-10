<?php
require '/code/spam/app/Models/Obfuscator.php';

$sData = "echo 'This is my PHP code, can be class class, interface, trait, etc. in PHP 5, 7, 7.2, 7.4 and higher.'";

$sObfusationData = new app\Models\Obfuscator($sData, 'Class/Code NAME');
file_put_contents('my_obfuscated_data.php', '<?php ' . "\r\n" . $sObfusationData);
