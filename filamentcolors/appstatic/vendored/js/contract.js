(function(){'use strict';var n=this,r=Date.now||function(){return+new Date};function t(c,g){c=c.split(".");var b=n;c[0]in b||!b.execScript||b.execScript("var "+c[0]);for(var a;c.length&&(a=c.shift());)c.length||void 0===g?b[a]&&b[a]!==Object.prototype[a]?b=b[a]:b=b[a]={}:b[a]=g};var u={};function z(c,g){return function(b){b||(b=window.event);return g.call(c,b)}}function A(c){c=c.target||c.srcElement;!c.getAttribute&&c.parentNode&&(c=c.parentNode);return c}var B="undefined"!=typeof navigator&&/Macintosh/.test(navigator.userAgent),C="undefined"!=typeof navigator&&!/Opera/.test(navigator.userAgent)&&/WebKit/.test(navigator.userAgent),D="undefined"!=typeof navigator&&!/Opera|WebKit/.test(navigator.userAgent)&&/Gecko/.test(navigator.product),E={A:1,INPUT:1,TEXTAREA:1,SELECT:1,BUTTON:1};
function F(){this._mouseEventsPrevented=!0}var G={A:13,BUTTON:0,CHECKBOX:32,COMBOBOX:13,GRIDCELL:13,LINK:13,LISTBOX:13,MENU:0,MENUBAR:0,MENUITEM:0,MENUITEMCHECKBOX:0,MENUITEMRADIO:0,OPTION:0,RADIO:32,RADIOGROUP:32,RESET:0,SUBMIT:0,TAB:0,TREE:13,TREEITEM:13};function I(c){return(c.getAttribute("type")||c.tagName).toUpperCase()in J}function K(c){return(c.getAttribute("type")||c.tagName).toUpperCase()in L}
var J={CHECKBOX:!0,OPTION:!0,RADIO:!0},L={COLOR:!0,DATE:!0,DATETIME:!0,"DATETIME-LOCAL":!0,EMAIL:!0,MONTH:!0,NUMBER:!0,PASSWORD:!0,RANGE:!0,SEARCH:!0,TEL:!0,TEXT:!0,TEXTAREA:!0,TIME:!0,URL:!0,WEEK:!0},M={A:!0,AREA:!0,BUTTON:!0,DIALOG:!0,IMG:!0,INPUT:!0,LINK:!0,MENU:!0,OPTGROUP:!0,OPTION:!0,PROGRESS:!0,SELECT:!0,TEXTAREA:!0};function N(){this.g=[];this.c=[];this.f={};this.a=null;this.b=[]}var O="undefined"!=typeof navigator&&/iPhone|iPad|iPod/.test(navigator.userAgent),P=String.prototype.trim?function(c){return c.trim()}:function(c){return c.replace(/^\s+/,"").replace(/\s+$/,"")},Q=/\s*;\s*/;
function R(c,g){return function(b){var a=g;if("click"==a&&(B&&b.metaKey||!B&&b.ctrlKey||2==b.which||null==b.which&&4==b.button||b.shiftKey))a="clickmod";else{var d=b.which||b.keyCode||b.key;C&&3==d&&(d=13);if(13!=d&&32!=d)d=!1;else{var f=A(b);var m=(f.getAttribute("role")||f.type||f.tagName).toUpperCase();var e;(e="keydown"!=b.type)||("getAttribute"in f?(e=(f.getAttribute("role")||f.tagName).toUpperCase(),e=!K(f)&&("COMBOBOX"!=e||"INPUT"!=e)&&!f.isContentEditable):e=!1,e=!e);(e=e||b.ctrlKey||b.shiftKey||
b.altKey||b.metaKey||I(f)&&32==d)||((e=f.tagName in E)||(e=f.getAttributeNode("tabindex"),e=!!e&&e.specified),e=!(e&&!f.disabled));e?d=!1:(f="INPUT"!=f.tagName.toUpperCase()||f.type,e=!(m in G)&&13==d,d=(!(G[m]%d)||e)&&!!f)}d&&(a="clickkey")}f=b.srcElement||b.target;d=S(a,b,f,"",null);for(m=f;m&&m!=this;m=m.__owner||m.parentNode){var k=m;var h=k;e=a;var l=h.__jsaction;if(!l){var p=null;"getAttribute"in h&&(p=h.getAttribute("jsaction"));if(p){l=u[p];if(!l){for(var l={},v=p.split(Q),w=0,T=v?v.length:
0;w<T;w++){var q=v[w];if(q){var x=q.indexOf(":"),H=-1!=x;var U=H?P(q.substr(0,x)):"click";l[U]=H?P(q.substr(x+1)):q}}u[p]=l}h.__jsaction=l}else l=V,h.__jsaction=l}"clickkey"==e?e="click":"click"!=e||l.click||(e="clickonly");h={h:e,action:l[e]||"",event:null,m:!1};if(h.m||h.action)break}h&&(d=S(h.h,h.event||b,f,h.action||"",k,d.timeStamp));d&&"touchend"==d.eventType&&(d.event._preventMouseEvents=F);if(h&&h.action){if(a="clickkey"==a)a=A(b),a=(a.type||a.tagName).toUpperCase(),(a=32==(b.which||b.keyCode||
b.key)&&"CHECKBOX"!=a)||(a=A(b),k=(a.getAttribute("role")||a.tagName).toUpperCase(),a=a.tagName.toUpperCase()in M&&"A"!=k&&!I(a)&&!K(a)||"BUTTON"==k);a&&(b.preventDefault?b.preventDefault():b.returnValue=!1)}else d.action="",d.actionElement=null;a=d;c.a&&(k=S(a.eventType,a.event,a.targetElement,a.action,a.actionElement,a.timeStamp),"clickonly"==k.eventType&&(k.eventType="click"),c.a(k,!0));if(a.actionElement){if(!D||"INPUT"!=a.targetElement.tagName&&"TEXTAREA"!=a.targetElement.tagName||"focus"!=a.eventType)b.stopPropagation?
b.stopPropagation():b.cancelBubble=!0;"A"!=a.actionElement.tagName||"click"!=a.eventType&&"clickmod"!=a.eventType||(b.preventDefault?b.preventDefault():b.returnValue=!1);if(c.a)c.a(a);else{if((k=n.document)&&!k.createEvent&&k.createEventObject)try{var y=k.createEventObject(b)}catch(Y){y=b}else y=b;a.event=y;c.b.push(a)}if("touchend"==a.event.type&&a.event._mouseEventsPrevented){b=a.event;for(var Z in b);r()}}}}
function S(c,g,b,a,d,f){return{eventType:c,event:g,targetElement:b,action:a,actionElement:d,timeStamp:f||r()}}var V={};function W(c,g){return function(b){var a=c,d=g,f=!1;"mouseenter"==a?a="mouseover":"mouseleave"==a&&(a="mouseout");if(b.addEventListener){if("focus"==a||"blur"==a||"error"==a||"load"==a)f=!0;b.addEventListener(a,d,f)}else b.attachEvent&&("focus"==a?a="focusin":"blur"==a&&(a="focusout"),d=z(b,d),b.attachEvent("on"+a,d));return{h:a,j:d,capture:f}}}
N.prototype.i=function(c,g){if(!this.f.hasOwnProperty(c)&&"mouseenter"!=c&&"mouseleave"!=c){var b=R(this,c);g=W(g||c,b);this.f[c]=b;this.g.push(g);for(b=0;b<this.c.length;++b){var a=this.c[b];a.b.push(g.call(null,a.a))}"click"==c&&this.i("keydown")}};N.prototype.j=function(c){return this.f[c]};N.prototype.l=function(c){c=new X(c);var g=c.a;O&&(g.style.cursor="pointer");for(g=0;g<this.g.length;++g)c.b.push(this.g[g].call(null,c.a));this.c.push(c);return c};
N.prototype.o=function(c){this.a=c;this.b&&(0<this.b.length&&c(this.b),this.b=null)};function X(c){this.a=c;this.b=[]};t("jsaction.EventContract",N);t("jsaction.EventContract.prototype.addContainer",N.prototype.l);t("jsaction.EventContract.prototype.addEvent",N.prototype.i);t("jsaction.EventContract.prototype.dispatchTo",N.prototype.o);}).call(this);

