# yfinance [![NPM version][npm-image]][npm-url] [![Build Status][travis-image]][travis-url] [![Dependency Status][daviddm-image]][daviddm-url] [![Coverage percentage][coveralls-image]][coveralls-url]
> Yahoo Finance API for NodeJs.

## Installation

```sh
$ npm install --save yfinance
```

## Usage

```js
var yfinance = require('yfinance');

yfinance.getQuotes('JNJ', function (err, data) {
    if(err) console.log(err);
    //...
});

yfinance.getHistorical('JNJ', '2016-08-01', '2016-08-05', function (err, data) {
    if(err) console.log(err);
    //...
});

yfinance.getDividendHistory('JNJ', '2015-01-01', '2015-12-31', function (err, data) {
    if(err) console.log(err);
    //... endDate not working!
});
```
## License

MIT © [Johan Carlsson]()


[npm-image]: https://badge.fury.io/js/yfinance.svg
[npm-url]: https://npmjs.org/package/yfinance
[travis-image]: https://travis-ci.org/johancn87/yf.svg?branch=master
[travis-url]: https://travis-ci.org/johancn87/yf
[daviddm-image]: https://david-dm.org/johancn87/yf.svg?theme=shields.io
[daviddm-url]: https://david-dm.org/johancn87/yf
[coveralls-image]: https://coveralls.io/repos/github/johancn87/yf/badge.svg?branch=master
[coveralls-url]: https://coveralls.io/github/johancn87/yf?branch=master
