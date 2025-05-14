/* A polyfill for browsers that don't support ligatures. */
/* The script tag referring to this file must be placed before the ending body tag. */

/* To provide support for elements dynamically added, this script adds
   method 'icomoonLiga' to the window object. You can pass element references to this method.
*/
(function () {
    'use strict';
    function supportsProperty(p) {
        var prefixes = ['Webkit', 'Moz', 'O', 'ms'],
            i,
            div = document.createElement('div'),
            ret = p in div.style;
        if (!ret) {
            p = p.charAt(0).toUpperCase() + p.substr(1);
            for (i = 0; i < prefixes.length; i += 1) {
                ret = prefixes[i] + p in div.style;
                if (ret) {
                    break;
                }
            }
        }
        return ret;
    }
    var icons;
    if (!supportsProperty('fontFeatureSettings')) {
        icons = {
            'copy': '&#xe92c;',
            'duplicate': '&#xe92c;',
            'floppy-disk': '&#xe962;',
            'save2': '&#xe962;',
            'attachment': '&#xe9cd;',
            'paperclip': '&#xe9cd;',
            'arrow-up-left': '&#xea31;',
            'up-left': '&#xea31;',
            'arrow-up': '&#xea32;',
            'up': '&#xea32;',
            'arrow-up-right': '&#xea33;',
            'up-right': '&#xea33;',
            'arrow-right': '&#xea34;',
            'right3': '&#xea34;',
            'arrow-down-right': '&#xea35;',
            'down-right': '&#xea35;',
            'arrow-down': '&#xea36;',
            'down': '&#xea36;',
            'arrow-down-left': '&#xea37;',
            'down-left': '&#xea37;',
            'arrow-left': '&#xea38;',
            'left3': '&#xea38;',
            'arrow-up-left2': '&#xea39;',
            'up-left2': '&#xea39;',
            'arrow-up2': '&#xea3a;',
            'up2': '&#xea3a;',
            'arrow-up-right2': '&#xea3b;',
            'up-right2': '&#xea3b;',
            'arrow-right2': '&#xea3c;',
            'right4': '&#xea3c;',
            'arrow-down-right2': '&#xea3d;',
            'down-right2': '&#xea3d;',
            'arrow-down2': '&#xea3e;',
            'down2': '&#xea3e;',
            'arrow-down-left2': '&#xea3f;',
            'down-left2': '&#xea3f;',
            'arrow-left2': '&#xea40;',
            'left4': '&#xea40;',
            'cancel-circle': '&#xea0d;',
            'close': '&#xea0d;',
            'radio-unchecked': '&#xea56;',
            'radio-button3': '&#xea56;',
            'search': '&#xe986;',
            'magnifier': '&#xe986;',
            'equalizer2': '&#xe993;',
            'sliders2': '&#xe993;',
          '0': 0
        };
        delete icons['0'];
        window.icomoonLiga = function (els) {
            var classes,
                el,
                i,
                innerHTML,
                key;
            els = els || document.getElementsByTagName('*');
            if (!els.length) {
                els = [els];
            }
            for (i = 0; ; i += 1) {
                el = els[i];
                if (!el) {
                    break;
                }
                classes = el.className;
                if (/icon-/.test(classes)) {
                    innerHTML = el.innerHTML;
                    if (innerHTML && innerHTML.length > 1) {
                        for (key in icons) {
                            if (icons.hasOwnProperty(key)) {
                                innerHTML = innerHTML.replace(new RegExp(key, 'g'), icons[key]);
                            }
                        }
                        el.innerHTML = innerHTML;
                    }
                }
            }
        };
        window.icomoonLiga();
    }
}());
