openssl req -new -newkey rsa:2048 -nodes -keyout med-voice-record.de.key -out med-voice-record.de.csr

You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:DE
State or Province Name (full name) [Some-State]:Hesse
Locality Name (eg, city) []:BadNauheim
Organization Name (eg, company) [Internet Widgits Pty Ltd]:FluidCareAI
Organizational Unit Name (eg, section) []:Technik
Common Name (e.g. server FQDN or YOUR name) []:med-voice-record.de
Email Address []:jana.beier2@gmail.com

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:jP3GjGsrURg99
An optional company name []:KerckhoffKlinik

root@ubuntu:~# cat med-voice-record.de.csr       

-----BEGIN CERTIFICATE REQUEST-----
MIIDIjCCAgoCAQAwgZ4xCzAJBgNVBAYTAkRFMQ4wDAYDVQQIDAVIZXNzZTETMBEG
A1UEBwwKQmFkTmF1aGVpbTEUMBIGA1UECgwLRmx1aWRDYXJlQUkxEDAOBgNVBAsM
B1RlY2huaWsxHDAaBgNVBAMME21lZC12b2ljZS1yZWNvcmQuZGUxJDAiBgkqhkiG
9w0BCQEWFWphbmEuYmVpZXIyQGdtYWlsLmNvbTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBAKdn59J0FYQWSCg8gtySgd3+ZVpX3+pQ2r8N0dEYWPZPNIP3
ko7AAw2iAIndT8p1nNXaoNEijdHwkHAK0gaZJKZFgrAAQ/eEfRwnYKPDhiCIjWFx
yWfxsWBTgBmuhziBLAurfIP/LSmLbChb/Ar8NdiWh/l2kBMR0hevUekGgoVx/XBb
kOEQiZzvE5ZUQ8QKUaSWzv1b3s0h2OliWmThdKfAl1QWmJg5rSOwSWH29w0VfQk6
6l9/ipkqiFJMPW0A50tZv9akqdacEgvCWsnOPSWzTgDZh79/ERNi/UKSEOJCzREL
3PTvgJRu006rdxj5CY+m4kfsKuwLVKRqD+voiWcCAwEAAaA+MBwGCSqGSIb3DQEJ
BzEPDA1qUDNHakdzclVSZzk5MB4GCSqGSIb3DQEJAjERDA9LZXJja2hvZmZLbGlu
aWswDQYJKoZIhvcNAQELBQADggEBAE+kWE1IWVQ6vaGslp8F2f07pmwSEWgsZD6R
AlTcRYr4mu4odN9wdXpfIsBTm2w2SN5j38ivMJ/U+T78AkilBH9qG+WfqW3ElNYp
jNwdTiaN/VI6fvdFlr3zGEcXE3gT6yRsCOcwPRawDJx/3dUpJuYa60ved1gdfq0D
zaEKE9VmjLDXBC2nOOwz+iFE0qIAPXN2PyjSX6Sf8AlXhmzcmvWfOsbLmRbGEkdj
wKtqCAwwPmRTyskQ7s3AVp8Pamqhbrknof3LYJBOfUPRi6T+bVUmRhe8VxMcaDdc
gyq0IsifE3P5cu+Xq2CBGZZ9vxgs2btFGQJRyv7Y/ycak/U2KQ8=
-----END CERTIFICATE REQUEST-----
