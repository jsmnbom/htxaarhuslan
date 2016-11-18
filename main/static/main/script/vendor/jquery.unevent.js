/*!
 * jquery.unevent.js [debounce] 0.4
 * https://github.com/yckart/jquery.unevent.js
 *
 * Copyright (c) 2012 Yannick Albert (http://yckart.com)
 * Licensed under the MIT license (http://www.opensource.org/licenses/mit-license.php).
 * 2013/07/27
 **/

;(function ($) {
    var on = $.fn.on, debounce;
    $.fn.on = function () {
        var args = Array.apply(null, arguments);
        var first = args[0];
        var last = args[args.length - 1];
        var isObj = typeof first === 'object';

        // we skip here if there's no delay given
        // or it is `1` (used internally)
        if (!isObj && isNaN(last) || (last === 1 && args.pop())) return on.apply(this, args);

        // recursive calling
        if (isObj) {
            for (var event in first) {
                this.on(event, last, first[event], args[1]);
            }
            return this;
        }

        // we store/remove the delay and handler-function
        var delay = args.pop();
        var fn = args.pop();

        // wrap and override the callback
        args.push(function () {
            var self = this, params = arguments;
            clearTimeout(debounce);
            debounce = setTimeout(function () {
                fn.apply(self, params);
            }, delay);
        });

        return on.apply(this, args);
    };
}(this.jQuery || this.Zepto));