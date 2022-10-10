<?php
/*
$raw_data = "imap://info@scottstainless.com:Scott6201+@box425.bluehost.com:993 | smtp://info@scottstainless.com:Scott6201+@box425.bluehost.com:465\n"
			// . "pop3://Dispatch@meyersturfandnursery.com:Meyersbobby!@mail.meyersturfandnursery.com:110/ |	smtp://Dispatch@meyersturfandnursery.com:Meyersbobby!@smtp.meyersturfandnursery.com:25/\n"
			// . "pop3://doug.burns:dlburns2@mail.insightbb.com:995/ |	smtp://doug.burns:dlburns2@mail.insightbb.com:587/\n"
			// . "imap://info@scottstainless.com|Scott6201+@box425.bluehost.com:993 | smtp://info@scottstainless.com:Scott6201+@box425.bluehost.com:465\n"
			;
// array of socks to insert
$data = [];

$unparsed_accs = explode("\n", $raw_data);
$proto_keys = array(
	"smtp" => array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port'),
	"pop3" => array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port'),
	"imap" => array('imap_login', 'imap_password', 'imap_host', 'imap_port'),
	"imap4" => array('imap_login', 'imap_password', 'imap_host', 'imap_port')
);
// $smtp_keys = array('smtp_login', 'smtp_password', 'smtp_host', 'smtp_port');
// $pop3_keys = array('pop3_login', 'pop3_password', 'pop3_host', 'pop3_port');
// $imap_keys = array('imap_login', 'imap_password', 'imap_host', 'imap_port');

foreach ($unparsed_accs as $raw_acc) {
	$data_acc = [];
    // all
    $raw_acc = trim($raw_acc);
    // check for
    if(strlen($raw_acc) < 1 ) continue 1;
    $protocols = preg_split("/\s\|\s/", $raw_acc);

    // var_dump($protocols);

    // preg_match_all('/((.{3,5})\:\/\/(.+)[\:|\|](.+)\@(.+)\:(\d{1,3})([\s\|\s]?)){1,5}/', $raw_acc, $matches);
    // preg_match_all('/([a-z]{3,5})\:\/\/([^\|\:\s]+)[\:\|](\S+)\@(\S+)\:(\d{1,5})/', $raw_acc, $matches);
    // var_dump($matches);

    foreach ($protocols as $proto) {
    	// encapsulate all in grous so that matches array will be more informative
    	// preg_match_all('/(.{3,5})\:\/\/(.+)\:(.+)\@(.+)\:(\d{1,3})/', $proto, $matches);
    	// slightly tuned regex for more preciciesly checks
    	preg_match_all('/([a-z0-9]{3,5})\:\/\/([^\|\:\s]+)[\:\|](\S+)\@(\S+)\:(\d{1,5})/', trim($proto), $matches);
    	// skip string that can't be parsed or parsed with some errors
    	if(count($matches) < 6) {
    		echo("Protocol rarsing give zero result for string:[{$proto}]\n");
    		continue 1;
    	}

    	$proto_key = trim($matches[1][0]);
    	echo("Parsed protocol:$proto_key\n");
    	if( !array_key_exists( $proto_key, $proto_keys ) ){
    		echo("Unexpected protocol:[{$proto_key}]\n");
    		continue 1;
    	}
    	$keys = $proto_keys[$proto_key];
    	foreach ($keys as $index => $field_name) {
    		$data_acc[$field_name] = trim($matches[$index+2][0]);
    	}
    }

    if(count($data_acc) >= 8){
    	$data[] = $data_acc;
    }else{
    	echo("data_acc[$raw_acc] had parsing errors, please check log above\n");
    }
}
*/

// // extract all occurencies
// preg_match_all('/.{3,5}\:\/\/.+\:.+\@.+\:\d{1,3}/', $acc_list, $matches);
// // echo "matches:\n";
// var_dump($matches);

// // check if we got anything in there
// if( !is_array( $matches[0] ) || count($matches[0]) == 0 ){
// 	echo "no shit\n";
// 	die();
// }

// // matches[0] contains whole string
// // matches[1] contains
// foreach ($matches[0] as $index=>$match) {
// 	echo "index:[{$index}] match:[{$match}]\n";
// 	if( $matches[1][$index] ){
// 		$credentials = $matches[1][$index];
// 		// extract credentials from whole string for futher ease of use
// 		$match = str_replace($credentials, "", $match);
// 		// remove @ from the end
// 		$credentials = substr($credentials,0,-1);
// 		echo "we got credentials:[$credentials]\n";
// 		echo "match now:[{$match}]\n";
// 		// host:port format
// 	    $ip_array = explode(":", $match);
// 	    // user:password format
// 	    $credentials = explode(":", $credentials);
// 	}else{
// 		$credentials = ['', ''];
// 	    $ip_array = explode(":",$match);
// 	}

//     // $data[] = [
//     // 	"host" => $ip_array[0],
//     // 	"port" => $ip_array[1],
//     // 	"user" => $credentials[0],
//     // 	"password" => $credentials[1] ];
// }


// $record="some name qwerty123@siduf.com";
// // /(?P<foo>abc)(.*)(?P<mail>([\w-\.]+)@((?:[\w]+\.)+)([a-zA-Z]{2,}))/
// preg_match_all("/([\w\s\'\"]+[\s]+)?[<|\'|\"]?(([\w-\.]+)@((?:[\w]+\.)+)([a-zA-Z]{2,}))?[>|\'|\"]?/", trim($record), $matches);
// $data = [
//     "name" => $matches[1][0],
//     "address" => $matches[1][0],
// ];

// // $data = $matches;

/*
$mail_preset = "(?P<mail>(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\]))";
$name_preset = "(?P<name>[\w\s(\"\')?]+)";
$company_preset = "(?P<company>[\w\s(\"\')?]+)";
$rest_preset = "(?P<rest>[\w\s(\"\')?]+)";
$relimiter_extractor = "(?:\])(.*?)(?:\[)";

$formatter = "[email] [name]";
$string = "hui@pizda.com some_shit name";

// create regexp from formatter
// stop0: remove whitespaces from string
$formatter = preg_replace("/\s/", "", $formatter);
// step1: replace delimiters with (\s?delimiter\s?) four backslashes are needed for escape value of $1
// $data = preg_replace("/(?:\])(.*?)(?:\[)/", "](\s?\\\\$1\s?)[", $formatter);
$start = -1;
$data = preg_replace_callback(
            "/(?:\])\s?(\S*?)\s?(?:\[)/",
            function($matches){
                echo("We got matches:");
                var_dump($matches);
                if(empty($matches[1]))
                    return '](\s)[';
                else
                    return '](\s?\\'.$matches[1].'\s?)[';
            },
            $formatter
        );
// spet2: replace email with pattern
$data = preg_replace("/\[e?mail\]/", $mail_preset, $data);
// // step3: replace name with pattern
$data = preg_replace("/\[name\]/", $name_preset, $data);
// // step4: replace company with pattern
$data = preg_replace("/\[company\]/", $company_preset, $data);
// // step5: replace rest with pattern
$data = preg_replace("/\[rest\]/", $rest_preset, $data);

// echo $data;

$parse_regex = "/".$data."/";

echo "regex:\n" . $parse_regex . "\n";

preg_match_all($parse_regex, $string, $matches);

// var_dump($matches);

$data = [
    "address" => array_key_exists("mail", $matches) ? $matches['mail'][0] : "",
    "name" => array_key_exists("name", $matches) ? $matches['name'][0] : "",
    "company" => array_key_exists("company", $matches) ? $matches['company'][0] : "",
    "rest" => array_key_exists("rest", $matches) ? $matches['rest'][0] : "",
];

echo "data:\n";
var_dump($data);
*/


// $attacth_path = 'file/upload/path/uploads/1g3PbKvJPWrFFRVET9dL7cW4Fpi7ZUHxMdI2PX6k.eot';

// $res = preg_match("/(\w+\.\w+)/i", $attacth_path, $matches);
// var_dump($res);
// var_dump($matches);

$rule_regex = "/(?P<r_3643425635>^accounts@)|(?P<r_2395738953>^news@)|(?P<r_3343527208>^postmaster@)|(?P<r_830113462>-reply)|(?P<r_3752704204>@gmail\.)|(?P<r_714395045>@googlegroups)|(?P<r_3057156693>@googlemail\.)|(?P<r_4186049316>\.@Aflac-OnlineServices\.)|(?P<r_2975674141>\.bg($|\s|;))|(?P<r_1460283427>\.br($|\s|;))|(?P<r_51437829>\.cz($|\s|;))|(?P<r_127663426>\.do($|\s|;))|(?P<r_2104958178>\.ee($|\s|;))|(?P<r_2971919207>\.gr($|\s|;))|(?P<r_3843973809>\.in($|\s|;))|(?P<r_1781219409>\.jp($|\s|;))|(?P<r_1673407569>\.ke($|\s|;))|(?P<r_2870936553>\.kr($|\s|;))|(?P<r_987324698>\.lt($|\s|;))|(?P<r_338643356>\.lv($|\s|;))|(?P<r_2104759354>\.mcdlv\.)|(?P<r_1912565311>\.mcsv\.)|(?P<r_273932309>\.pl($|\s|;))|(?P<r_2700003231>\.rsgsv\.)|(?P<r_145607520>\.rsys2\.)|(?P<r_348505090>\.ru($|\s|;))|(?P<r_2667919071>\.sk($|\s|;))|(?P<r_2109397388>\.tr($|\s|;))|(?P<r_925736131>\.tw($|\s|;))|(?P<r_120966150>\.ua($|\s|;))|(?P<r_867940564>\.vn($|\s|;))|(?P<r_4131297163>\.za($|\s|;))|(?P<r_702852208>\.zw($|\s|;))|(?P<r_2885317286>donotreply)|(?P<r_1630462537>no-response)|(?P<r_2228053172>noreply)|(?P<r_3120047367>youtube\.)/i";
$address = "4207-551@tonami.co.jp";
$res = preg_match($rule_regex, $address, $matches);

var_dump($res);
var_dump($matches);
