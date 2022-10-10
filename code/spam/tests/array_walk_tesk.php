<?php
echo("begin.\r\n");

$a1 = [];
$a2 = [];
$a3 = [];

$mails = ["aa1", "bb1", "cc1", "aa2", "bb2", "cc2", "aa3", "bb3", "cc3", "aa4", "bb4", "cc4"];

array_walk($mails, function($item) use (&$a1, &$a2, &$a3)
{
	echo("walkig item:{$item}\r\n");
	if( strpos($item, "a") !== false ){
		// $a1[] = $item;
		array_push($a1, $item);
	}elseif (strpos($item, "b") !== false ) {
		$a2[] = $item;
	}elseif (strpos($item, "c") !== false ) {
		$a3[] = $item;
	}
});

var_dump($a1);
