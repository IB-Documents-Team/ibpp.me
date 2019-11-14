# ibpp.me Link Shortener

##  Usage

Run the API on a host with Docker.    
Embed the JavaScript and HTML found in `/embed-snippet/` some CSS
and have the URL it's posting to match the host:port that the API
is running on.

## API

**Get redirected to page**    
`GET /<shortened_uri>`    
Response: 301 or 404 (redirect or not found)

**Shorten URL**    
`POST /function/shorten`    
Sample response (200):
```json
{
    "url": "https://ibpp.me/abc123"
}
```
or 403 (permission denied)

Permission will be denied if the host you are `post`ing from is not
a whitelisted domain in the API's configuration.


## License

This project is licensed under the [GNU GPLv3](https://www.gnu.org/licenses/gpl.html).    
This license is copy-left and conducive to free, open-source software.

Project license: https://github.com/IB-Documents-Team/ibpp.me/blob/master/LICENSE.md    
License details: https://choosealicense.com/licenses/gpl-3.0/#
