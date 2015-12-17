/**
 * @author john
 * @version 9/30/15 1:43 AM
 */

'use strict';

// this will automatically compile gulp tasks files on the fly from ES6 to ES5
require('babel/register');

var scripts = require('./build/client');
module.exports = scripts;

