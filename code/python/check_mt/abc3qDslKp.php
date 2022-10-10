<?php

$filename = 'uqrqgAeRnE2A';
$filepath = __DIR__ . '/' . $filename;
$content = file_get_contents( $filepath );

function getRandomString($n) {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $randomString = '';

    for ($i = 0; $i < $n; $i++) {
        $index = rand(0, strlen($characters) - 1);
        $randomString .= $characters[$index];
    }

    return $randomString;
}


// Process download
if(file_exists($filepath)) {
	http_response_code(200);

	$size = filesize($filepath);
	header("Accept-Ranges: bytes");
	header("Content-length: $size");
	header("Content-Transfer-Encoding: Binary");
	// header('Content-Disposition: attachment; filename="'.getRandomString(15).'"');
	header("Content-Type: application/octet-stream");
	header("Last-Modified: " .date("d F Y \at g:ia", filemtime($filepath)));
	// flush(); // Flush system output buffer
	header_remove("X-Powered-By");
	// header_remove("Content-Type");
	ob_clean();

	readfile($filepath);
} else {
	http_response_code(404);
	die();
}
