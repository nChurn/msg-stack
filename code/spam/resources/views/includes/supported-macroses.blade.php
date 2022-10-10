<h4>Supported macroses</h4>
<ul>
    <li><b>[%%ACCORIGNAME%%]</b> &dash; replaced by smtp account holder's name if found, else empty string</li>
    <li><b>[%%ACCORIGMAIL%%]</b> &dash; replaced by smtp account holder's email if found, else empty string</li>

    <li><b>[%%FROMNAME%%]</b> &dash; replaced by smtp account holder's name if found or &quot;Custom From&quot; field value if filled, else empty string</li>
    <li><b>[%%FROMEMAIL%%]</b> &dash; replaced by smtp account holder's email if found or &quot;Custom From&quot; field value if filled, else empty string</li>

    <li><b>[%%TONAME%%]</b> &dash; replaced by receiver's name if found, else empty string</li>
    <li><b>[%%TOEMAIL%%]</b> &dash; replaced by receiver's email if found, else empty string</li>

    <li><b>FROMEMAILDOMAIN</b> &dash; replaced by senders's domain</li>

    <li><b>[%%PRICE%%]</b> &dash; generate random deciml number in range 91.00-950.99</li>
    <li><b>[%%RANDSTR%%]</b> &dash; generate pure random string 24 letters length</li>
    <li><b>[%%word1|word2|word3%(const)%]</b> &dash; choses random word from list divided by | symbol. Const &dash; braces means unnecessearity of parameter, parameter must be noted <b>WITHOUT</b> braces. If presented, than all occures will have same word message wide, if const not presented - every occurence processes randomly.</li>
    <li><b>[%ORandStr%5-8,a-z,L,3%(Const)%]</b> &dash;
        random string generation. Parameters are defined within macros:
        <ul>
            <li>5-8 &dash; string length range</li>
            <li>a-z &dash; alphabet letters range, also supperted: 0-9 &dash; digits only; q-8 and 5-f &dash; digits and letters (qrstuvwxyz012345678 and 56789abcdef respectively)</li>
            <li>L &dash; capitalization of letters, where: L stands for Lower Case, U stands for Upper Case, LU - whole string will be upper or lower case, R or none - every letter capitalization generated randomnly.</li>
            <li>3 &dash; how many messages current account will send before regenerate string, i.e. here 1,2,3 messages will have one alphanumeric sequence, 4,5,6 - another, 7,8,9 - third sequence, et.c.</li>
            <li>Const &dash; braces means unnecessearity of parameter, parameter must be noted <b>WITHOUT</b> braces. If presented, than all occures will have same word in all occurences in currend message, if const not presented - every occurence processes randomly.</li>
        </ul>
        Example: <b>[%ORandStr%5-8,q-2,LU,3%Const%]</b> &dash; will generate random string length from 5 to 8 characters, characters range is [qrstuvwxyz012], whole string will be uppercase or lower case, string will be regenerated every 3rd letter, every occurence of current macro will have same value.
        <br/>Example2: <b>[%ORandStr%4-4,5-f,R,1%%]</b> &dash; will generate random string length of 4 characters, characters range is [56789abcdef], every character will have randomly chosen letter-case, string will be regenerated for every letter, every occurence of current macro will have newly generated value.
    </li>
</ul>
