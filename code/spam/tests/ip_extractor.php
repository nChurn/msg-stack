<?php
$ip_list = "u53r:p@ssw0rd@192.179.8.1:9909a 127.0.0.1:32a42\r\npizdec";
// array of socks to insert
$data = [];

// extract all occurencies
preg_match_all('/((.+\:.+)?\@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}\s/', $ip_list, $matches);
// echo "matches:\n";
// var_dump($matches);

// check if we got anything in there
if( !is_array( $matches[0] ) || count($matches[0]) == 0 ){
	echo "no shit\n";
	die();
}

// matches[0] contains whole string
// matches[1] contains 
foreach ($matches[0] as $index=>$match) {
	echo "index:[{$index}] match:[{$match}]\n";
	if( $matches[1][$index] ){
		$credentials = $matches[1][$index];
		// extract credentials from whole string for futher ease of use
		$match = str_replace($credentials, "", $match);
		// remove @ from the end
		$credentials = substr($credentials,0,-1);
		echo "we got credentials:[$credentials]\n";
		echo "match now:[{$match}]\n";
		// host:port format
	    $ip_array = explode(":", $match);
	    // user:password format
	    $credentials = explode(":", $credentials);
	}else{
		$credentials = ['', ''];
	    $ip_array = explode(":",$match);
	}

    $data[] = [
    	"host" => $ip_array[0], 
    	"port" => $ip_array[1], 
    	"user" => $credentials[0], 
    	"password" => $credentials[1] ];
}

echo "data:\n";
var_dump($data);
?>