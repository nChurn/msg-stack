<?php

$fname = 'test.txt';
$fpath = __DIR__ . '/' . $fname;
$content = file_get_contents( $fpath );
$content .= "\n" . $_SERVER['HTTP_USER_AGENT'];

$content = trim($content) . "\n";
file_put_contents($fpath, $content );
echo('404 not found');

// typical user agent:
// Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E; Tablet PC 2.0)
