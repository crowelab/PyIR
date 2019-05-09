#!/usr/bin/perl  -w


use strict;
my $inputfile=shift (@ARGV);

open(in_handle, $inputfile);

while(my $line=<in_handle>){
 #print ("line = $line\n");
  if ($line =~ /^>.*\|(TR.+)\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|.*\|$/){

    print(">$1\n");

  } elsif ($line =~ /^>[\w\d\-\*\\\/\(\)\@\!\`\~\#\$\%\^\&]*\|(Homsap_)?(IG[\w\d\-\*\/\\\(\)\&\^\%\$\#\@\!\~\`]+)\|((.*)?\|?)*/ ){
#

    print(">$2\n");

  } else {

    $line =~ s/\.+//g;
    #get rid of dot
    print("$line");

  }
}

close (in_handle);
