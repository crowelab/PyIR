#!/usr/bin/perl  -w


use strict;
my $inputfile=shift (@ARGV);

open(in_handle, $inputfile);

while(my $line=<in_handle>){
 #print ("line = $line\n");
  if ($line =~ /^>.*\|(TR.+)\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|/){
    print(">$1\n");
  } elsif ($line =~ /^>.*\|(IG.+)\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|/){
    print(">$1\n");
  } else {
    $line =~ s/\.+//g;
    #get rid of dot
    print("$line");
  }
}

close (in_handle);




# There was a time when the initial setup script's test cases were failing due to a naming convention not being upheld in one of the soruce files.
# 
#
#
# old naming convention
#>AB019437|IGHV7-81*01|Homo sapiens|ORF|V-REGION|6456..6751|296 nt|1| | | | |296+24=320| | |
# naming conventiont that was used that one time that broke stuff
#>AB019438|Homsap_IGHV8-51-1*01|Homo sapiens|IGHV8|P|V-REGION
#
#
# regex that corrected the erro -- This regex will also work with the correct naming convention but we decided to stick with the default perl script that was provided by NCBI
#elsif ($line =~ /^>[\w\d\-\*\\\/\(\)\@\!\`\~\#\$\%\^\&]*\|(Homsap_)?(IG[\w\d\-\*\/\\\(\)\&\^\%\$\#\@\!\~\`]+)\|.*/ ){
#print(">$2\n");
#}
#
