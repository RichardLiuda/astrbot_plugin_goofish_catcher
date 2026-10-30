(()=>{var JO=Object.create;var ru=Object.defineProperty;var eN=Object.getOwnPropertyDescriptor;var tN=Object.getOwnPropertyNames;var rN=Object.getPrototypeOf,oN=Object.prototype.hasOwnProperty;var et=(e,t)=>()=>(e&&(t=e(e=0)),t);var se=(e,t)=>()=>(t||e((t={exports:{}}).exports,t),t.exports),ou=(e,t)=>{for(var r in t)ru(e,r,{get:t[r],enumerable:!0})},ib=(e,t,r,o)=>{if(t&&typeof t=="object"||typeof t=="function")for(let n of tN(t))!oN.call(e,n)&&n!==r&&ru(e,n,{get:()=>t[n],enumerable:!(o=eN(t,n))||o.enumerable});return e};var P=(e,t,r)=>(r=e!=null?JO(rN(e)):{},ib(t||!e||!e.__esModule?ru(r,"default",{value:e,enumerable:!0}):r,e)),oa=e=>ib(ru({},"__esModule",{value:!0}),e);var vb=se(xe=>{"use strict";var Zl=Symbol.for("react.element"),nN=Symbol.for("react.portal"),sN=Symbol.for("react.fragment"),iN=Symbol.for("react.strict_mode"),aN=Symbol.for("react.profiler"),lN=Symbol.for("react.provider"),pN=Symbol.for("react.context"),cN=Symbol.for("react.forward_ref"),uN=Symbol.for("react.suspense"),dN=Symbol.for("react.memo"),fN=Symbol.for("react.lazy"),ab=Symbol.iterator;function mN(e){return e===null||typeof e!="object"?null:(e=ab&&e[ab]||e["@@iterator"],typeof e=="function"?e:null)}var cb={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},ub=Object.assign,db={};function na(e,t,r){this.props=e,this.context=t,this.refs=db,this.updater=r||cb}na.prototype.isReactComponent={};na.prototype.setState=function(e,t){if(typeof e!="object"&&typeof e!="function"&&e!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,e,t,"setState")};na.prototype.forceUpdate=function(e){this.updater.enqueueForceUpdate(this,e,"forceUpdate")};function fb(){}fb.prototype=na.prototype;function yy(e,t,r){this.props=e,this.context=t,this.refs=db,this.updater=r||cb}var hy=yy.prototype=new fb;hy.constructor=yy;ub(hy,na.prototype);hy.isPureReactComponent=!0;var lb=Array.isArray,mb=Object.prototype.hasOwnProperty,gy={current:null},yb={key:!0,ref:!0,__self:!0,__source:!0};function hb(e,t,r){var o,n={},s=null,i=null;if(t!=null)for(o in t.ref!==void 0&&(i=t.ref),t.key!==void 0&&(s=""+t.key),t)mb.call(t,o)&&!yb.hasOwnProperty(o)&&(n[o]=t[o]);var a=arguments.length-2;if(a===1)n.children=r;else if(1<a){for(var l=Array(a),p=0;p<a;p++)l[p]=arguments[p+2];n.children=l}if(e&&e.defaultProps)for(o in a=e.defaultProps,a)n[o]===void 0&&(n[o]=a[o]);return{$$typeof:Zl,type:e,key:s,ref:i,props:n,_owner:gy.current}}function yN(e,t){return{$$typeof:Zl,type:e.type,key:t,ref:e.ref,props:e.props,_owner:e._owner}}function vy(e){return typeof e=="object"&&e!==null&&e.$$typeof===Zl}function hN(e){var t={"=":"=0",":":"=2"};return"$"+e.replace(/[=:]/g,function(r){return t[r]})}var pb=/\/+/g;function my(e,t){return typeof e=="object"&&e!==null&&e.key!=null?hN(""+e.key):t.toString(36)}function su(e,t,r,o,n){var s=typeof e;(s==="undefined"||s==="boolean")&&(e=null);var i=!1;if(e===null)i=!0;else switch(s){case"string":case"number":i=!0;break;case"object":switch(e.$$typeof){case Zl:case nN:i=!0}}if(i)return i=e,n=n(i),e=o===""?"."+my(i,0):o,lb(n)?(r="",e!=null&&(r=e.replace(pb,"$&/")+"/"),su(n,t,r,"",function(p){return p})):n!=null&&(vy(n)&&(n=yN(n,r+(!n.key||i&&i.key===n.key?"":(""+n.key).replace(pb,"$&/")+"/")+e)),t.push(n)),1;if(i=0,o=o===""?".":o+":",lb(e))for(var a=0;a<e.length;a++){s=e[a];var l=o+my(s,a);i+=su(s,t,r,l,n)}else if(l=mN(e),typeof l=="function")for(e=l.call(e),a=0;!(s=e.next()).done;)s=s.value,l=o+my(s,a++),i+=su(s,t,r,l,n);else if(s==="object")throw t=String(e),Error("Objects are not valid as a React child (found: "+(t==="[object Object]"?"object with keys {"+Object.keys(e).join(", ")+"}":t)+"). If you meant to render a collection of children, use an array instead.");return i}function nu(e,t,r){if(e==null)return e;var o=[],n=0;return su(e,o,"","",function(s){return t.call(r,s,n++)}),o}function gN(e){if(e._status===-1){var t=e._result;t=t(),t.then(function(r){(e._status===0||e._status===-1)&&(e._status=1,e._result=r)},function(r){(e._status===0||e._status===-1)&&(e._status=2,e._result=r)}),e._status===-1&&(e._status=0,e._result=t)}if(e._status===1)return e._result.default;throw e._result}var gr={current:null},iu={transition:null},vN={ReactCurrentDispatcher:gr,ReactCurrentBatchConfig:iu,ReactCurrentOwner:gy};function gb(){throw Error("act(...) is not supported in production builds of React.")}xe.Children={map:nu,forEach:function(e,t,r){nu(e,function(){t.apply(this,arguments)},r)},count:function(e){var t=0;return nu(e,function(){t++}),t},toArray:function(e){return nu(e,function(t){return t})||[]},only:function(e){if(!vy(e))throw Error("React.Children.only expected to receive a single React element child.");return e}};xe.Component=na;xe.Fragment=sN;xe.Profiler=aN;xe.PureComponent=yy;xe.StrictMode=iN;xe.Suspense=uN;xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=vN;xe.act=gb;xe.cloneElement=function(e,t,r){if(e==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+e+".");var o=ub({},e.props),n=e.key,s=e.ref,i=e._owner;if(t!=null){if(t.ref!==void 0&&(s=t.ref,i=gy.current),t.key!==void 0&&(n=""+t.key),e.type&&e.type.defaultProps)var a=e.type.defaultProps;for(l in t)mb.call(t,l)&&!yb.hasOwnProperty(l)&&(o[l]=t[l]===void 0&&a!==void 0?a[l]:t[l])}var l=arguments.length-2;if(l===1)o.children=r;else if(1<l){a=Array(l);for(var p=0;p<l;p++)a[p]=arguments[p+2];o.children=a}return{$$typeof:Zl,type:e.type,key:n,ref:s,props:o,_owner:i}};xe.createContext=function(e){return e={$$typeof:pN,_currentValue:e,_currentValue2:e,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},e.Provider={$$typeof:lN,_context:e},e.Consumer=e};xe.createElement=hb;xe.createFactory=function(e){var t=hb.bind(null,e);return t.type=e,t};xe.createRef=function(){return{current:null}};xe.forwardRef=function(e){return{$$typeof:cN,render:e}};xe.isValidElement=vy;xe.lazy=function(e){return{$$typeof:fN,_payload:{_status:-1,_result:e},_init:gN}};xe.memo=function(e,t){return{$$typeof:dN,type:e,compare:t===void 0?null:t}};xe.startTransition=function(e){var t=iu.transition;iu.transition={};try{e()}finally{iu.transition=t}};xe.unstable_act=gb;xe.useCallback=function(e,t){return gr.current.useCallback(e,t)};xe.useContext=function(e){return gr.current.useContext(e)};xe.useDebugValue=function(){};xe.useDeferredValue=function(e){return gr.current.useDeferredValue(e)};xe.useEffect=function(e,t){return gr.current.useEffect(e,t)};xe.useId=function(){return gr.current.useId()};xe.useImperativeHandle=function(e,t,r){return gr.current.useImperativeHandle(e,t,r)};xe.useInsertionEffect=function(e,t){return gr.current.useInsertionEffect(e,t)};xe.useLayoutEffect=function(e,t){return gr.current.useLayoutEffect(e,t)};xe.useMemo=function(e,t){return gr.current.useMemo(e,t)};xe.useReducer=function(e,t,r){return gr.current.useReducer(e,t,r)};xe.useRef=function(e){return gr.current.useRef(e)};xe.useState=function(e){return gr.current.useState(e)};xe.useSyncExternalStore=function(e,t,r){return gr.current.useSyncExternalStore(e,t,r)};xe.useTransition=function(){return gr.current.useTransition()};xe.version="18.3.1"});var L=se((AW,xb)=>{"use strict";xb.exports=vb()});var Sb=se(Ve=>{"use strict";function Py(e,t){var r=e.length;e.push(t);e:for(;0<r;){var o=r-1>>>1,n=e[o];if(0<au(n,t))e[o]=t,e[r]=n,r=o;else break e}}function Do(e){return e.length===0?null:e[0]}function pu(e){if(e.length===0)return null;var t=e[0],r=e.pop();if(r!==t){e[0]=r;e:for(var o=0,n=e.length,s=n>>>1;o<s;){var i=2*(o+1)-1,a=e[i],l=i+1,p=e[l];if(0>au(a,r))l<n&&0>au(p,a)?(e[o]=p,e[l]=r,o=l):(e[o]=a,e[i]=r,o=i);else if(l<n&&0>au(p,r))e[o]=p,e[l]=r,o=l;else break e}}return t}function au(e,t){var r=e.sortIndex-t.sortIndex;return r!==0?r:e.id-t.id}typeof performance=="object"&&typeof performance.now=="function"?(Tb=performance,Ve.unstable_now=function(){return Tb.now()}):(xy=Date,bb=xy.now(),Ve.unstable_now=function(){return xy.now()-bb});var Tb,xy,bb,on=[],Qn=[],xN=1,io=null,nr=3,cu=!1,Ws=!1,ep=!1,$b=typeof setTimeout=="function"?setTimeout:null,wb=typeof clearTimeout=="function"?clearTimeout:null,Pb=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function Cy(e){for(var t=Do(Qn);t!==null;){if(t.callback===null)pu(Qn);else if(t.startTime<=e)pu(Qn),t.sortIndex=t.expirationTime,Py(on,t);else break;t=Do(Qn)}}function $y(e){if(ep=!1,Cy(e),!Ws)if(Do(on)!==null)Ws=!0,_y(wy);else{var t=Do(Qn);t!==null&&Ry($y,t.startTime-e)}}function wy(e,t){Ws=!1,ep&&(ep=!1,wb(tp),tp=-1),cu=!0;var r=nr;try{for(Cy(t),io=Do(on);io!==null&&(!(io.expirationTime>t)||e&&!Eb());){var o=io.callback;if(typeof o=="function"){io.callback=null,nr=io.priorityLevel;var n=o(io.expirationTime<=t);t=Ve.unstable_now(),typeof n=="function"?io.callback=n:io===Do(on)&&pu(on),Cy(t)}else pu(on);io=Do(on)}if(io!==null)var s=!0;else{var i=Do(Qn);i!==null&&Ry($y,i.startTime-t),s=!1}return s}finally{io=null,nr=r,cu=!1}}var uu=!1,lu=null,tp=-1,_b=5,Rb=-1;function Eb(){return!(Ve.unstable_now()-Rb<_b)}function Ty(){if(lu!==null){var e=Ve.unstable_now();Rb=e;var t=!0;try{t=lu(!0,e)}finally{t?Jl():(uu=!1,lu=null)}}else uu=!1}var Jl;typeof Pb=="function"?Jl=function(){Pb(Ty)}:typeof MessageChannel<"u"?(by=new MessageChannel,Cb=by.port2,by.port1.onmessage=Ty,Jl=function(){Cb.postMessage(null)}):Jl=function(){$b(Ty,0)};var by,Cb;function _y(e){lu=e,uu||(uu=!0,Jl())}function Ry(e,t){tp=$b(function(){e(Ve.unstable_now())},t)}Ve.unstable_IdlePriority=5;Ve.unstable_ImmediatePriority=1;Ve.unstable_LowPriority=4;Ve.unstable_NormalPriority=3;Ve.unstable_Profiling=null;Ve.unstable_UserBlockingPriority=2;Ve.unstable_cancelCallback=function(e){e.callback=null};Ve.unstable_continueExecution=function(){Ws||cu||(Ws=!0,_y(wy))};Ve.unstable_forceFrameRate=function(e){0>e||125<e?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):_b=0<e?Math.floor(1e3/e):5};Ve.unstable_getCurrentPriorityLevel=function(){return nr};Ve.unstable_getFirstCallbackNode=function(){return Do(on)};Ve.unstable_next=function(e){switch(nr){case 1:case 2:case 3:var t=3;break;default:t=nr}var r=nr;nr=t;try{return e()}finally{nr=r}};Ve.unstable_pauseExecution=function(){};Ve.unstable_requestPaint=function(){};Ve.unstable_runWithPriority=function(e,t){switch(e){case 1:case 2:case 3:case 4:case 5:break;default:e=3}var r=nr;nr=e;try{return t()}finally{nr=r}};Ve.unstable_scheduleCallback=function(e,t,r){var o=Ve.unstable_now();switch(typeof r=="object"&&r!==null?(r=r.delay,r=typeof r=="number"&&0<r?o+r:o):r=o,e){case 1:var n=-1;break;case 2:n=250;break;case 5:n=1073741823;break;case 4:n=1e4;break;default:n=5e3}return n=r+n,e={id:xN++,callback:t,priorityLevel:e,startTime:r,expirationTime:n,sortIndex:-1},r>o?(e.sortIndex=r,Py(Qn,e),Do(on)===null&&e===Do(Qn)&&(ep?(wb(tp),tp=-1):ep=!0,Ry($y,r-o))):(e.sortIndex=n,Py(on,e),Ws||cu||(Ws=!0,_y(wy))),e};Ve.unstable_shouldYield=Eb;Ve.unstable_wrapCallback=function(e){var t=nr;return function(){var r=nr;nr=t;try{return e.apply(this,arguments)}finally{nr=r}}}});var Ob=se((BW,kb)=>{"use strict";kb.exports=Sb()});var j1=se(Zr=>{"use strict";var TN=L(),Xr=Ob();function ee(e){for(var t="https://reactjs.org/docs/error-decoder.html?invariant="+e,r=1;r<arguments.length;r++)t+="&args[]="+encodeURIComponent(arguments[r]);return"Minified React error #"+e+"; visit "+t+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var A0=new Set,Cp={};function ri(e,t){wa(e,t),wa(e+"Capture",t)}function wa(e,t){for(Cp[e]=t,e=0;e<t.length;e++)A0.add(t[e])}var wn=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),Xy=Object.prototype.hasOwnProperty,bN=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,Nb={},Mb={};function PN(e){return Xy.call(Mb,e)?!0:Xy.call(Nb,e)?!1:bN.test(e)?Mb[e]=!0:(Nb[e]=!0,!1)}function CN(e,t,r,o){if(r!==null&&r.type===0)return!1;switch(typeof t){case"function":case"symbol":return!0;case"boolean":return o?!1:r!==null?!r.acceptsBooleans:(e=e.toLowerCase().slice(0,5),e!=="data-"&&e!=="aria-");default:return!1}}function $N(e,t,r,o){if(t===null||typeof t>"u"||CN(e,t,r,o))return!0;if(o)return!1;if(r!==null)switch(r.type){case 3:return!t;case 4:return t===!1;case 5:return isNaN(t);case 6:return isNaN(t)||1>t}return!1}function Tr(e,t,r,o,n,s,i){this.acceptsBooleans=t===2||t===3||t===4,this.attributeName=o,this.attributeNamespace=n,this.mustUseProperty=r,this.propertyName=e,this.type=t,this.sanitizeURL=s,this.removeEmptyString=i}var Zt={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e){Zt[e]=new Tr(e,0,!1,e,null,!1,!1)});[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(e){var t=e[0];Zt[t]=new Tr(t,1,!1,e[1],null,!1,!1)});["contentEditable","draggable","spellCheck","value"].forEach(function(e){Zt[e]=new Tr(e,2,!1,e.toLowerCase(),null,!1,!1)});["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(e){Zt[e]=new Tr(e,2,!1,e,null,!1,!1)});"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e){Zt[e]=new Tr(e,3,!1,e.toLowerCase(),null,!1,!1)});["checked","multiple","muted","selected"].forEach(function(e){Zt[e]=new Tr(e,3,!0,e,null,!1,!1)});["capture","download"].forEach(function(e){Zt[e]=new Tr(e,4,!1,e,null,!1,!1)});["cols","rows","size","span"].forEach(function(e){Zt[e]=new Tr(e,6,!1,e,null,!1,!1)});["rowSpan","start"].forEach(function(e){Zt[e]=new Tr(e,5,!1,e.toLowerCase(),null,!1,!1)});var Uh=/[\-:]([a-z])/g;function Wh(e){return e[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e){var t=e.replace(Uh,Wh);Zt[t]=new Tr(t,1,!1,e,null,!1,!1)});"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e){var t=e.replace(Uh,Wh);Zt[t]=new Tr(t,1,!1,e,"http://www.w3.org/1999/xlink",!1,!1)});["xml:base","xml:lang","xml:space"].forEach(function(e){var t=e.replace(Uh,Wh);Zt[t]=new Tr(t,1,!1,e,"http://www.w3.org/XML/1998/namespace",!1,!1)});["tabIndex","crossOrigin"].forEach(function(e){Zt[e]=new Tr(e,1,!1,e.toLowerCase(),null,!1,!1)});Zt.xlinkHref=new Tr("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1);["src","href","action","formAction"].forEach(function(e){Zt[e]=new Tr(e,1,!1,e.toLowerCase(),null,!0,!0)});function Vh(e,t,r,o){var n=Zt.hasOwnProperty(t)?Zt[t]:null;(n!==null?n.type!==0:o||!(2<t.length)||t[0]!=="o"&&t[0]!=="O"||t[1]!=="n"&&t[1]!=="N")&&($N(t,r,n,o)&&(r=null),o||n===null?PN(t)&&(r===null?e.removeAttribute(t):e.setAttribute(t,""+r)):n.mustUseProperty?e[n.propertyName]=r===null?n.type===3?!1:"":r:(t=n.attributeName,o=n.attributeNamespace,r===null?e.removeAttribute(t):(n=n.type,r=n===3||n===4&&r===!0?"":""+r,o?e.setAttributeNS(o,t,r):e.setAttribute(t,r))))}var Sn=TN.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,du=Symbol.for("react.element"),aa=Symbol.for("react.portal"),la=Symbol.for("react.fragment"),Hh=Symbol.for("react.strict_mode"),Qy=Symbol.for("react.profiler"),z0=Symbol.for("react.provider"),B0=Symbol.for("react.context"),qh=Symbol.for("react.forward_ref"),Zy=Symbol.for("react.suspense"),Jy=Symbol.for("react.suspense_list"),Kh=Symbol.for("react.memo"),Jn=Symbol.for("react.lazy");Symbol.for("react.scope");Symbol.for("react.debug_trace_mode");var F0=Symbol.for("react.offscreen");Symbol.for("react.legacy_hidden");Symbol.for("react.cache");Symbol.for("react.tracing_marker");var Ib=Symbol.iterator;function rp(e){return e===null||typeof e!="object"?null:(e=Ib&&e[Ib]||e["@@iterator"],typeof e=="function"?e:null)}var lt=Object.assign,Ey;function cp(e){if(Ey===void 0)try{throw Error()}catch(r){var t=r.stack.trim().match(/\n( *(at )?)/);Ey=t&&t[1]||""}return`
`+Ey+e}var Sy=!1;function ky(e,t){if(!e||Sy)return"";Sy=!0;var r=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(t)if(t=function(){throw Error()},Object.defineProperty(t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(t,[])}catch(p){var o=p}Reflect.construct(e,[],t)}else{try{t.call()}catch(p){o=p}e.call(t.prototype)}else{try{throw Error()}catch(p){o=p}e()}}catch(p){if(p&&o&&typeof p.stack=="string"){for(var n=p.stack.split(`
`),s=o.stack.split(`
`),i=n.length-1,a=s.length-1;1<=i&&0<=a&&n[i]!==s[a];)a--;for(;1<=i&&0<=a;i--,a--)if(n[i]!==s[a]){if(i!==1||a!==1)do if(i--,a--,0>a||n[i]!==s[a]){var l=`
`+n[i].replace(" at new "," at ");return e.displayName&&l.includes("<anonymous>")&&(l=l.replace("<anonymous>",e.displayName)),l}while(1<=i&&0<=a);break}}}finally{Sy=!1,Error.prepareStackTrace=r}return(e=e?e.displayName||e.name:"")?cp(e):""}function wN(e){switch(e.tag){case 5:return cp(e.type);case 16:return cp("Lazy");case 13:return cp("Suspense");case 19:return cp("SuspenseList");case 0:case 2:case 15:return e=ky(e.type,!1),e;case 11:return e=ky(e.type.render,!1),e;case 1:return e=ky(e.type,!0),e;default:return""}}function eh(e){if(e==null)return null;if(typeof e=="function")return e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case la:return"Fragment";case aa:return"Portal";case Qy:return"Profiler";case Hh:return"StrictMode";case Zy:return"Suspense";case Jy:return"SuspenseList"}if(typeof e=="object")switch(e.$$typeof){case B0:return(e.displayName||"Context")+".Consumer";case z0:return(e._context.displayName||"Context")+".Provider";case qh:var t=e.render;return e=e.displayName,e||(e=t.displayName||t.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case Kh:return t=e.displayName||null,t!==null?t:eh(e.type)||"Memo";case Jn:t=e._payload,e=e._init;try{return eh(e(t))}catch{}}return null}function _N(e){var t=e.type;switch(e.tag){case 24:return"Cache";case 9:return(t.displayName||"Context")+".Consumer";case 10:return(t._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return e=t.render,e=e.displayName||e.name||"",t.displayName||(e!==""?"ForwardRef("+e+")":"ForwardRef");case 7:return"Fragment";case 5:return t;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return eh(t);case 8:return t===Hh?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof t=="function")return t.displayName||t.name||null;if(typeof t=="string")return t}return null}function fs(e){switch(typeof e){case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function U0(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(t==="checkbox"||t==="radio")}function RN(e){var t=U0(e)?"checked":"value",r=Object.getOwnPropertyDescriptor(e.constructor.prototype,t),o=""+e[t];if(!e.hasOwnProperty(t)&&typeof r<"u"&&typeof r.get=="function"&&typeof r.set=="function"){var n=r.get,s=r.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return n.call(this)},set:function(i){o=""+i,s.call(this,i)}}),Object.defineProperty(e,t,{enumerable:r.enumerable}),{getValue:function(){return o},setValue:function(i){o=""+i},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function fu(e){e._valueTracker||(e._valueTracker=RN(e))}function W0(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var r=t.getValue(),o="";return e&&(o=U0(e)?e.checked?"true":"false":e.value),e=o,e!==r?(t.setValue(e),!0):!1}function Fu(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}function th(e,t){var r=t.checked;return lt({},t,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:r??e._wrapperState.initialChecked})}function jb(e,t){var r=t.defaultValue==null?"":t.defaultValue,o=t.checked!=null?t.checked:t.defaultChecked;r=fs(t.value!=null?t.value:r),e._wrapperState={initialChecked:o,initialValue:r,controlled:t.type==="checkbox"||t.type==="radio"?t.checked!=null:t.value!=null}}function V0(e,t){t=t.checked,t!=null&&Vh(e,"checked",t,!1)}function rh(e,t){V0(e,t);var r=fs(t.value),o=t.type;if(r!=null)o==="number"?(r===0&&e.value===""||e.value!=r)&&(e.value=""+r):e.value!==""+r&&(e.value=""+r);else if(o==="submit"||o==="reset"){e.removeAttribute("value");return}t.hasOwnProperty("value")?oh(e,t.type,r):t.hasOwnProperty("defaultValue")&&oh(e,t.type,fs(t.defaultValue)),t.checked==null&&t.defaultChecked!=null&&(e.defaultChecked=!!t.defaultChecked)}function Db(e,t,r){if(t.hasOwnProperty("value")||t.hasOwnProperty("defaultValue")){var o=t.type;if(!(o!=="submit"&&o!=="reset"||t.value!==void 0&&t.value!==null))return;t=""+e._wrapperState.initialValue,r||t===e.value||(e.value=t),e.defaultValue=t}r=e.name,r!==""&&(e.name=""),e.defaultChecked=!!e._wrapperState.initialChecked,r!==""&&(e.name=r)}function oh(e,t,r){(t!=="number"||Fu(e.ownerDocument)!==e)&&(r==null?e.defaultValue=""+e._wrapperState.initialValue:e.defaultValue!==""+r&&(e.defaultValue=""+r))}var up=Array.isArray;function xa(e,t,r,o){if(e=e.options,t){t={};for(var n=0;n<r.length;n++)t["$"+r[n]]=!0;for(r=0;r<e.length;r++)n=t.hasOwnProperty("$"+e[r].value),e[r].selected!==n&&(e[r].selected=n),n&&o&&(e[r].defaultSelected=!0)}else{for(r=""+fs(r),t=null,n=0;n<e.length;n++){if(e[n].value===r){e[n].selected=!0,o&&(e[n].defaultSelected=!0);return}t!==null||e[n].disabled||(t=e[n])}t!==null&&(t.selected=!0)}}function nh(e,t){if(t.dangerouslySetInnerHTML!=null)throw Error(ee(91));return lt({},t,{value:void 0,defaultValue:void 0,children:""+e._wrapperState.initialValue})}function Lb(e,t){var r=t.value;if(r==null){if(r=t.children,t=t.defaultValue,r!=null){if(t!=null)throw Error(ee(92));if(up(r)){if(1<r.length)throw Error(ee(93));r=r[0]}t=r}t==null&&(t=""),r=t}e._wrapperState={initialValue:fs(r)}}function H0(e,t){var r=fs(t.value),o=fs(t.defaultValue);r!=null&&(r=""+r,r!==e.value&&(e.value=r),t.defaultValue==null&&e.defaultValue!==r&&(e.defaultValue=r)),o!=null&&(e.defaultValue=""+o)}function Ab(e){var t=e.textContent;t===e._wrapperState.initialValue&&t!==""&&t!==null&&(e.value=t)}function q0(e){switch(e){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function sh(e,t){return e==null||e==="http://www.w3.org/1999/xhtml"?q0(t):e==="http://www.w3.org/2000/svg"&&t==="foreignObject"?"http://www.w3.org/1999/xhtml":e}var mu,K0=(function(e){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(t,r,o,n){MSApp.execUnsafeLocalFunction(function(){return e(t,r,o,n)})}:e})(function(e,t){if(e.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in e)e.innerHTML=t;else{for(mu=mu||document.createElement("div"),mu.innerHTML="<svg>"+t.valueOf().toString()+"</svg>",t=mu.firstChild;e.firstChild;)e.removeChild(e.firstChild);for(;t.firstChild;)e.appendChild(t.firstChild)}});function $p(e,t){if(t){var r=e.firstChild;if(r&&r===e.lastChild&&r.nodeType===3){r.nodeValue=t;return}}e.textContent=t}var mp={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},EN=["Webkit","ms","Moz","O"];Object.keys(mp).forEach(function(e){EN.forEach(function(t){t=t+e.charAt(0).toUpperCase()+e.substring(1),mp[t]=mp[e]})});function G0(e,t,r){return t==null||typeof t=="boolean"||t===""?"":r||typeof t!="number"||t===0||mp.hasOwnProperty(e)&&mp[e]?(""+t).trim():t+"px"}function Y0(e,t){e=e.style;for(var r in t)if(t.hasOwnProperty(r)){var o=r.indexOf("--")===0,n=G0(r,t[r],o);r==="float"&&(r="cssFloat"),o?e.setProperty(r,n):e[r]=n}}var SN=lt({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function ih(e,t){if(t){if(SN[e]&&(t.children!=null||t.dangerouslySetInnerHTML!=null))throw Error(ee(137,e));if(t.dangerouslySetInnerHTML!=null){if(t.children!=null)throw Error(ee(60));if(typeof t.dangerouslySetInnerHTML!="object"||!("__html"in t.dangerouslySetInnerHTML))throw Error(ee(61))}if(t.style!=null&&typeof t.style!="object")throw Error(ee(62))}}function ah(e,t){if(e.indexOf("-")===-1)return typeof t.is=="string";switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var lh=null;function Gh(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var ph=null,Ta=null,ba=null;function zb(e){if(e=Up(e)){if(typeof ph!="function")throw Error(ee(280));var t=e.stateNode;t&&(t=yd(t),ph(e.stateNode,e.type,t))}}function X0(e){Ta?ba?ba.push(e):ba=[e]:Ta=e}function Q0(){if(Ta){var e=Ta,t=ba;if(ba=Ta=null,zb(e),t)for(e=0;e<t.length;e++)zb(t[e])}}function Z0(e,t){return e(t)}function J0(){}var Oy=!1;function eP(e,t,r){if(Oy)return e(t,r);Oy=!0;try{return Z0(e,t,r)}finally{Oy=!1,(Ta!==null||ba!==null)&&(J0(),Q0())}}function wp(e,t){var r=e.stateNode;if(r===null)return null;var o=yd(r);if(o===null)return null;r=o[t];e:switch(t){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(o=!o.disabled)||(e=e.type,o=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!o;break e;default:e=!1}if(e)return null;if(r&&typeof r!="function")throw Error(ee(231,t,typeof r));return r}var ch=!1;if(wn)try{sa={},Object.defineProperty(sa,"passive",{get:function(){ch=!0}}),window.addEventListener("test",sa,sa),window.removeEventListener("test",sa,sa)}catch{ch=!1}var sa;function kN(e,t,r,o,n,s,i,a,l){var p=Array.prototype.slice.call(arguments,3);try{t.apply(r,p)}catch(c){this.onError(c)}}var yp=!1,Uu=null,Wu=!1,uh=null,ON={onError:function(e){yp=!0,Uu=e}};function NN(e,t,r,o,n,s,i,a,l){yp=!1,Uu=null,kN.apply(ON,arguments)}function MN(e,t,r,o,n,s,i,a,l){if(NN.apply(this,arguments),yp){if(yp){var p=Uu;yp=!1,Uu=null}else throw Error(ee(198));Wu||(Wu=!0,uh=p)}}function oi(e){var t=e,r=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,(t.flags&4098)!==0&&(r=t.return),e=t.return;while(e)}return t.tag===3?r:null}function tP(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function Bb(e){if(oi(e)!==e)throw Error(ee(188))}function IN(e){var t=e.alternate;if(!t){if(t=oi(e),t===null)throw Error(ee(188));return t!==e?null:e}for(var r=e,o=t;;){var n=r.return;if(n===null)break;var s=n.alternate;if(s===null){if(o=n.return,o!==null){r=o;continue}break}if(n.child===s.child){for(s=n.child;s;){if(s===r)return Bb(n),e;if(s===o)return Bb(n),t;s=s.sibling}throw Error(ee(188))}if(r.return!==o.return)r=n,o=s;else{for(var i=!1,a=n.child;a;){if(a===r){i=!0,r=n,o=s;break}if(a===o){i=!0,o=n,r=s;break}a=a.sibling}if(!i){for(a=s.child;a;){if(a===r){i=!0,r=s,o=n;break}if(a===o){i=!0,o=s,r=n;break}a=a.sibling}if(!i)throw Error(ee(189))}}if(r.alternate!==o)throw Error(ee(190))}if(r.tag!==3)throw Error(ee(188));return r.stateNode.current===r?e:t}function rP(e){return e=IN(e),e!==null?oP(e):null}function oP(e){if(e.tag===5||e.tag===6)return e;for(e=e.child;e!==null;){var t=oP(e);if(t!==null)return t;e=e.sibling}return null}var nP=Xr.unstable_scheduleCallback,Fb=Xr.unstable_cancelCallback,jN=Xr.unstable_shouldYield,DN=Xr.unstable_requestPaint,xt=Xr.unstable_now,LN=Xr.unstable_getCurrentPriorityLevel,Yh=Xr.unstable_ImmediatePriority,sP=Xr.unstable_UserBlockingPriority,Vu=Xr.unstable_NormalPriority,AN=Xr.unstable_LowPriority,iP=Xr.unstable_IdlePriority,ud=null,ln=null;function zN(e){if(ln&&typeof ln.onCommitFiberRoot=="function")try{ln.onCommitFiberRoot(ud,e,void 0,(e.current.flags&128)===128)}catch{}}var Fo=Math.clz32?Math.clz32:UN,BN=Math.log,FN=Math.LN2;function UN(e){return e>>>=0,e===0?32:31-(BN(e)/FN|0)|0}var yu=64,hu=4194304;function dp(e){switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return e&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return e&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return e}}function Hu(e,t){var r=e.pendingLanes;if(r===0)return 0;var o=0,n=e.suspendedLanes,s=e.pingedLanes,i=r&268435455;if(i!==0){var a=i&~n;a!==0?o=dp(a):(s&=i,s!==0&&(o=dp(s)))}else i=r&~n,i!==0?o=dp(i):s!==0&&(o=dp(s));if(o===0)return 0;if(t!==0&&t!==o&&(t&n)===0&&(n=o&-o,s=t&-t,n>=s||n===16&&(s&4194240)!==0))return t;if((o&4)!==0&&(o|=r&16),t=e.entangledLanes,t!==0)for(e=e.entanglements,t&=o;0<t;)r=31-Fo(t),n=1<<r,o|=e[r],t&=~n;return o}function WN(e,t){switch(e){case 1:case 2:case 4:return t+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function VN(e,t){for(var r=e.suspendedLanes,o=e.pingedLanes,n=e.expirationTimes,s=e.pendingLanes;0<s;){var i=31-Fo(s),a=1<<i,l=n[i];l===-1?((a&r)===0||(a&o)!==0)&&(n[i]=WN(a,t)):l<=t&&(e.expiredLanes|=a),s&=~a}}function dh(e){return e=e.pendingLanes&-1073741825,e!==0?e:e&1073741824?1073741824:0}function aP(){var e=yu;return yu<<=1,(yu&4194240)===0&&(yu=64),e}function Ny(e){for(var t=[],r=0;31>r;r++)t.push(e);return t}function Bp(e,t,r){e.pendingLanes|=t,t!==536870912&&(e.suspendedLanes=0,e.pingedLanes=0),e=e.eventTimes,t=31-Fo(t),e[t]=r}function HN(e,t){var r=e.pendingLanes&~t;e.pendingLanes=t,e.suspendedLanes=0,e.pingedLanes=0,e.expiredLanes&=t,e.mutableReadLanes&=t,e.entangledLanes&=t,t=e.entanglements;var o=e.eventTimes;for(e=e.expirationTimes;0<r;){var n=31-Fo(r),s=1<<n;t[n]=0,o[n]=-1,e[n]=-1,r&=~s}}function Xh(e,t){var r=e.entangledLanes|=t;for(e=e.entanglements;r;){var o=31-Fo(r),n=1<<o;n&t|e[o]&t&&(e[o]|=t),r&=~n}}var De=0;function lP(e){return e&=-e,1<e?4<e?(e&268435455)!==0?16:536870912:4:1}var pP,Qh,cP,uP,dP,fh=!1,gu=[],ss=null,is=null,as=null,_p=new Map,Rp=new Map,ts=[],qN="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function Ub(e,t){switch(e){case"focusin":case"focusout":ss=null;break;case"dragenter":case"dragleave":is=null;break;case"mouseover":case"mouseout":as=null;break;case"pointerover":case"pointerout":_p.delete(t.pointerId);break;case"gotpointercapture":case"lostpointercapture":Rp.delete(t.pointerId)}}function op(e,t,r,o,n,s){return e===null||e.nativeEvent!==s?(e={blockedOn:t,domEventName:r,eventSystemFlags:o,nativeEvent:s,targetContainers:[n]},t!==null&&(t=Up(t),t!==null&&Qh(t)),e):(e.eventSystemFlags|=o,t=e.targetContainers,n!==null&&t.indexOf(n)===-1&&t.push(n),e)}function KN(e,t,r,o,n){switch(t){case"focusin":return ss=op(ss,e,t,r,o,n),!0;case"dragenter":return is=op(is,e,t,r,o,n),!0;case"mouseover":return as=op(as,e,t,r,o,n),!0;case"pointerover":var s=n.pointerId;return _p.set(s,op(_p.get(s)||null,e,t,r,o,n)),!0;case"gotpointercapture":return s=n.pointerId,Rp.set(s,op(Rp.get(s)||null,e,t,r,o,n)),!0}return!1}function fP(e){var t=qs(e.target);if(t!==null){var r=oi(t);if(r!==null){if(t=r.tag,t===13){if(t=tP(r),t!==null){e.blockedOn=t,dP(e.priority,function(){cP(r)});return}}else if(t===3&&r.stateNode.current.memoizedState.isDehydrated){e.blockedOn=r.tag===3?r.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Ou(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var r=mh(e.domEventName,e.eventSystemFlags,t[0],e.nativeEvent);if(r===null){r=e.nativeEvent;var o=new r.constructor(r.type,r);lh=o,r.target.dispatchEvent(o),lh=null}else return t=Up(r),t!==null&&Qh(t),e.blockedOn=r,!1;t.shift()}return!0}function Wb(e,t,r){Ou(e)&&r.delete(t)}function GN(){fh=!1,ss!==null&&Ou(ss)&&(ss=null),is!==null&&Ou(is)&&(is=null),as!==null&&Ou(as)&&(as=null),_p.forEach(Wb),Rp.forEach(Wb)}function np(e,t){e.blockedOn===t&&(e.blockedOn=null,fh||(fh=!0,Xr.unstable_scheduleCallback(Xr.unstable_NormalPriority,GN)))}function Ep(e){function t(n){return np(n,e)}if(0<gu.length){np(gu[0],e);for(var r=1;r<gu.length;r++){var o=gu[r];o.blockedOn===e&&(o.blockedOn=null)}}for(ss!==null&&np(ss,e),is!==null&&np(is,e),as!==null&&np(as,e),_p.forEach(t),Rp.forEach(t),r=0;r<ts.length;r++)o=ts[r],o.blockedOn===e&&(o.blockedOn=null);for(;0<ts.length&&(r=ts[0],r.blockedOn===null);)fP(r),r.blockedOn===null&&ts.shift()}var Pa=Sn.ReactCurrentBatchConfig,qu=!0;function YN(e,t,r,o){var n=De,s=Pa.transition;Pa.transition=null;try{De=1,Zh(e,t,r,o)}finally{De=n,Pa.transition=s}}function XN(e,t,r,o){var n=De,s=Pa.transition;Pa.transition=null;try{De=4,Zh(e,t,r,o)}finally{De=n,Pa.transition=s}}function Zh(e,t,r,o){if(qu){var n=mh(e,t,r,o);if(n===null)zy(e,t,o,Ku,r),Ub(e,o);else if(KN(n,e,t,r,o))o.stopPropagation();else if(Ub(e,o),t&4&&-1<qN.indexOf(e)){for(;n!==null;){var s=Up(n);if(s!==null&&pP(s),s=mh(e,t,r,o),s===null&&zy(e,t,o,Ku,r),s===n)break;n=s}n!==null&&o.stopPropagation()}else zy(e,t,o,null,r)}}var Ku=null;function mh(e,t,r,o){if(Ku=null,e=Gh(o),e=qs(e),e!==null)if(t=oi(e),t===null)e=null;else if(r=t.tag,r===13){if(e=tP(t),e!==null)return e;e=null}else if(r===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null);return Ku=e,null}function mP(e){switch(e){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(LN()){case Yh:return 1;case sP:return 4;case Vu:case AN:return 16;case iP:return 536870912;default:return 16}default:return 16}}var os=null,Jh=null,Nu=null;function yP(){if(Nu)return Nu;var e,t=Jh,r=t.length,o,n="value"in os?os.value:os.textContent,s=n.length;for(e=0;e<r&&t[e]===n[e];e++);var i=r-e;for(o=1;o<=i&&t[r-o]===n[s-o];o++);return Nu=n.slice(e,1<o?1-o:void 0)}function Mu(e){var t=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function vu(){return!0}function Vb(){return!1}function Qr(e){function t(r,o,n,s,i){this._reactName=r,this._targetInst=n,this.type=o,this.nativeEvent=s,this.target=i,this.currentTarget=null;for(var a in e)e.hasOwnProperty(a)&&(r=e[a],this[a]=r?r(s):s[a]);return this.isDefaultPrevented=(s.defaultPrevented!=null?s.defaultPrevented:s.returnValue===!1)?vu:Vb,this.isPropagationStopped=Vb,this}return lt(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var r=this.nativeEvent;r&&(r.preventDefault?r.preventDefault():typeof r.returnValue!="unknown"&&(r.returnValue=!1),this.isDefaultPrevented=vu)},stopPropagation:function(){var r=this.nativeEvent;r&&(r.stopPropagation?r.stopPropagation():typeof r.cancelBubble!="unknown"&&(r.cancelBubble=!0),this.isPropagationStopped=vu)},persist:function(){},isPersistent:vu}),t}var Na={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},eg=Qr(Na),Fp=lt({},Na,{view:0,detail:0}),QN=Qr(Fp),My,Iy,sp,dd=lt({},Fp,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:tg,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==sp&&(sp&&e.type==="mousemove"?(My=e.screenX-sp.screenX,Iy=e.screenY-sp.screenY):Iy=My=0,sp=e),My)},movementY:function(e){return"movementY"in e?e.movementY:Iy}}),Hb=Qr(dd),ZN=lt({},dd,{dataTransfer:0}),JN=Qr(ZN),e2=lt({},Fp,{relatedTarget:0}),jy=Qr(e2),t2=lt({},Na,{animationName:0,elapsedTime:0,pseudoElement:0}),r2=Qr(t2),o2=lt({},Na,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),n2=Qr(o2),s2=lt({},Na,{data:0}),qb=Qr(s2),i2={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},a2={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},l2={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function p2(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=l2[e])?!!t[e]:!1}function tg(){return p2}var c2=lt({},Fp,{key:function(e){if(e.key){var t=i2[e.key]||e.key;if(t!=="Unidentified")return t}return e.type==="keypress"?(e=Mu(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?a2[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:tg,charCode:function(e){return e.type==="keypress"?Mu(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Mu(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),u2=Qr(c2),d2=lt({},dd,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Kb=Qr(d2),f2=lt({},Fp,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:tg}),m2=Qr(f2),y2=lt({},Na,{propertyName:0,elapsedTime:0,pseudoElement:0}),h2=Qr(y2),g2=lt({},dd,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),v2=Qr(g2),x2=[9,13,27,32],rg=wn&&"CompositionEvent"in window,hp=null;wn&&"documentMode"in document&&(hp=document.documentMode);var T2=wn&&"TextEvent"in window&&!hp,hP=wn&&(!rg||hp&&8<hp&&11>=hp),Gb=" ",Yb=!1;function gP(e,t){switch(e){case"keyup":return x2.indexOf(t.keyCode)!==-1;case"keydown":return t.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function vP(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var pa=!1;function b2(e,t){switch(e){case"compositionend":return vP(t);case"keypress":return t.which!==32?null:(Yb=!0,Gb);case"textInput":return e=t.data,e===Gb&&Yb?null:e;default:return null}}function P2(e,t){if(pa)return e==="compositionend"||!rg&&gP(e,t)?(e=yP(),Nu=Jh=os=null,pa=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case"compositionend":return hP&&t.locale!=="ko"?null:t.data;default:return null}}var C2={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Xb(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t==="input"?!!C2[e.type]:t==="textarea"}function xP(e,t,r,o){X0(o),t=Gu(t,"onChange"),0<t.length&&(r=new eg("onChange","change",null,r,o),e.push({event:r,listeners:t}))}var gp=null,Sp=null;function $2(e){kP(e,0)}function fd(e){var t=da(e);if(W0(t))return e}function w2(e,t){if(e==="change")return t}var TP=!1;wn&&(wn?(Tu="oninput"in document,Tu||(Dy=document.createElement("div"),Dy.setAttribute("oninput","return;"),Tu=typeof Dy.oninput=="function"),xu=Tu):xu=!1,TP=xu&&(!document.documentMode||9<document.documentMode));var xu,Tu,Dy;function Qb(){gp&&(gp.detachEvent("onpropertychange",bP),Sp=gp=null)}function bP(e){if(e.propertyName==="value"&&fd(Sp)){var t=[];xP(t,Sp,e,Gh(e)),eP($2,t)}}function _2(e,t,r){e==="focusin"?(Qb(),gp=t,Sp=r,gp.attachEvent("onpropertychange",bP)):e==="focusout"&&Qb()}function R2(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return fd(Sp)}function E2(e,t){if(e==="click")return fd(t)}function S2(e,t){if(e==="input"||e==="change")return fd(t)}function k2(e,t){return e===t&&(e!==0||1/e===1/t)||e!==e&&t!==t}var Wo=typeof Object.is=="function"?Object.is:k2;function kp(e,t){if(Wo(e,t))return!0;if(typeof e!="object"||e===null||typeof t!="object"||t===null)return!1;var r=Object.keys(e),o=Object.keys(t);if(r.length!==o.length)return!1;for(o=0;o<r.length;o++){var n=r[o];if(!Xy.call(t,n)||!Wo(e[n],t[n]))return!1}return!0}function Zb(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function Jb(e,t){var r=Zb(e);e=0;for(var o;r;){if(r.nodeType===3){if(o=e+r.textContent.length,e<=t&&o>=t)return{node:r,offset:t-e};e=o}e:{for(;r;){if(r.nextSibling){r=r.nextSibling;break e}r=r.parentNode}r=void 0}r=Zb(r)}}function PP(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?PP(e,t.parentNode):"contains"in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function CP(){for(var e=window,t=Fu();t instanceof e.HTMLIFrameElement;){try{var r=typeof t.contentWindow.location.href=="string"}catch{r=!1}if(r)e=t.contentWindow;else break;t=Fu(e.document)}return t}function og(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||t==="textarea"||e.contentEditable==="true")}function O2(e){var t=CP(),r=e.focusedElem,o=e.selectionRange;if(t!==r&&r&&r.ownerDocument&&PP(r.ownerDocument.documentElement,r)){if(o!==null&&og(r)){if(t=o.start,e=o.end,e===void 0&&(e=t),"selectionStart"in r)r.selectionStart=t,r.selectionEnd=Math.min(e,r.value.length);else if(e=(t=r.ownerDocument||document)&&t.defaultView||window,e.getSelection){e=e.getSelection();var n=r.textContent.length,s=Math.min(o.start,n);o=o.end===void 0?s:Math.min(o.end,n),!e.extend&&s>o&&(n=o,o=s,s=n),n=Jb(r,s);var i=Jb(r,o);n&&i&&(e.rangeCount!==1||e.anchorNode!==n.node||e.anchorOffset!==n.offset||e.focusNode!==i.node||e.focusOffset!==i.offset)&&(t=t.createRange(),t.setStart(n.node,n.offset),e.removeAllRanges(),s>o?(e.addRange(t),e.extend(i.node,i.offset)):(t.setEnd(i.node,i.offset),e.addRange(t)))}}for(t=[],e=r;e=e.parentNode;)e.nodeType===1&&t.push({element:e,left:e.scrollLeft,top:e.scrollTop});for(typeof r.focus=="function"&&r.focus(),r=0;r<t.length;r++)e=t[r],e.element.scrollLeft=e.left,e.element.scrollTop=e.top}}var N2=wn&&"documentMode"in document&&11>=document.documentMode,ca=null,yh=null,vp=null,hh=!1;function e0(e,t,r){var o=r.window===r?r.document:r.nodeType===9?r:r.ownerDocument;hh||ca==null||ca!==Fu(o)||(o=ca,"selectionStart"in o&&og(o)?o={start:o.selectionStart,end:o.selectionEnd}:(o=(o.ownerDocument&&o.ownerDocument.defaultView||window).getSelection(),o={anchorNode:o.anchorNode,anchorOffset:o.anchorOffset,focusNode:o.focusNode,focusOffset:o.focusOffset}),vp&&kp(vp,o)||(vp=o,o=Gu(yh,"onSelect"),0<o.length&&(t=new eg("onSelect","select",null,t,r),e.push({event:t,listeners:o}),t.target=ca)))}function bu(e,t){var r={};return r[e.toLowerCase()]=t.toLowerCase(),r["Webkit"+e]="webkit"+t,r["Moz"+e]="moz"+t,r}var ua={animationend:bu("Animation","AnimationEnd"),animationiteration:bu("Animation","AnimationIteration"),animationstart:bu("Animation","AnimationStart"),transitionend:bu("Transition","TransitionEnd")},Ly={},$P={};wn&&($P=document.createElement("div").style,"AnimationEvent"in window||(delete ua.animationend.animation,delete ua.animationiteration.animation,delete ua.animationstart.animation),"TransitionEvent"in window||delete ua.transitionend.transition);function md(e){if(Ly[e])return Ly[e];if(!ua[e])return e;var t=ua[e],r;for(r in t)if(t.hasOwnProperty(r)&&r in $P)return Ly[e]=t[r];return e}var wP=md("animationend"),_P=md("animationiteration"),RP=md("animationstart"),EP=md("transitionend"),SP=new Map,t0="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function ys(e,t){SP.set(e,t),ri(t,[e])}for(Pu=0;Pu<t0.length;Pu++)Cu=t0[Pu],r0=Cu.toLowerCase(),o0=Cu[0].toUpperCase()+Cu.slice(1),ys(r0,"on"+o0);var Cu,r0,o0,Pu;ys(wP,"onAnimationEnd");ys(_P,"onAnimationIteration");ys(RP,"onAnimationStart");ys("dblclick","onDoubleClick");ys("focusin","onFocus");ys("focusout","onBlur");ys(EP,"onTransitionEnd");wa("onMouseEnter",["mouseout","mouseover"]);wa("onMouseLeave",["mouseout","mouseover"]);wa("onPointerEnter",["pointerout","pointerover"]);wa("onPointerLeave",["pointerout","pointerover"]);ri("onChange","change click focusin focusout input keydown keyup selectionchange".split(" "));ri("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" "));ri("onBeforeInput",["compositionend","keypress","textInput","paste"]);ri("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" "));ri("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" "));ri("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var fp="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),M2=new Set("cancel close invalid load scroll toggle".split(" ").concat(fp));function n0(e,t,r){var o=e.type||"unknown-event";e.currentTarget=r,MN(o,t,void 0,e),e.currentTarget=null}function kP(e,t){t=(t&4)!==0;for(var r=0;r<e.length;r++){var o=e[r],n=o.event;o=o.listeners;e:{var s=void 0;if(t)for(var i=o.length-1;0<=i;i--){var a=o[i],l=a.instance,p=a.currentTarget;if(a=a.listener,l!==s&&n.isPropagationStopped())break e;n0(n,a,p),s=l}else for(i=0;i<o.length;i++){if(a=o[i],l=a.instance,p=a.currentTarget,a=a.listener,l!==s&&n.isPropagationStopped())break e;n0(n,a,p),s=l}}}if(Wu)throw e=uh,Wu=!1,uh=null,e}function Ge(e,t){var r=t[bh];r===void 0&&(r=t[bh]=new Set);var o=e+"__bubble";r.has(o)||(OP(t,e,2,!1),r.add(o))}function Ay(e,t,r){var o=0;t&&(o|=4),OP(r,e,o,t)}var $u="_reactListening"+Math.random().toString(36).slice(2);function Op(e){if(!e[$u]){e[$u]=!0,A0.forEach(function(r){r!=="selectionchange"&&(M2.has(r)||Ay(r,!1,e),Ay(r,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[$u]||(t[$u]=!0,Ay("selectionchange",!1,t))}}function OP(e,t,r,o){switch(mP(t)){case 1:var n=YN;break;case 4:n=XN;break;default:n=Zh}r=n.bind(null,t,r,e),n=void 0,!ch||t!=="touchstart"&&t!=="touchmove"&&t!=="wheel"||(n=!0),o?n!==void 0?e.addEventListener(t,r,{capture:!0,passive:n}):e.addEventListener(t,r,!0):n!==void 0?e.addEventListener(t,r,{passive:n}):e.addEventListener(t,r,!1)}function zy(e,t,r,o,n){var s=o;if((t&1)===0&&(t&2)===0&&o!==null)e:for(;;){if(o===null)return;var i=o.tag;if(i===3||i===4){var a=o.stateNode.containerInfo;if(a===n||a.nodeType===8&&a.parentNode===n)break;if(i===4)for(i=o.return;i!==null;){var l=i.tag;if((l===3||l===4)&&(l=i.stateNode.containerInfo,l===n||l.nodeType===8&&l.parentNode===n))return;i=i.return}for(;a!==null;){if(i=qs(a),i===null)return;if(l=i.tag,l===5||l===6){o=s=i;continue e}a=a.parentNode}}o=o.return}eP(function(){var p=s,c=Gh(r),u=[];e:{var f=SP.get(e);if(f!==void 0){var v=eg,x=e;switch(e){case"keypress":if(Mu(r)===0)break e;case"keydown":case"keyup":v=u2;break;case"focusin":x="focus",v=jy;break;case"focusout":x="blur",v=jy;break;case"beforeblur":case"afterblur":v=jy;break;case"click":if(r.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":v=Hb;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":v=JN;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":v=m2;break;case wP:case _P:case RP:v=r2;break;case EP:v=h2;break;case"scroll":v=QN;break;case"wheel":v=v2;break;case"copy":case"cut":case"paste":v=n2;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":v=Kb}var h=(t&4)!==0,b=!h&&e==="scroll",y=h?f!==null?f+"Capture":null:f;h=[];for(var m=p,g;m!==null;){g=m;var T=g.stateNode;if(g.tag===5&&T!==null&&(g=T,y!==null&&(T=wp(m,y),T!=null&&h.push(Np(m,T,g)))),b)break;m=m.return}0<h.length&&(f=new v(f,x,null,r,c),u.push({event:f,listeners:h}))}}if((t&7)===0){e:{if(f=e==="mouseover"||e==="pointerover",v=e==="mouseout"||e==="pointerout",f&&r!==lh&&(x=r.relatedTarget||r.fromElement)&&(qs(x)||x[_n]))break e;if((v||f)&&(f=c.window===c?c:(f=c.ownerDocument)?f.defaultView||f.parentWindow:window,v?(x=r.relatedTarget||r.toElement,v=p,x=x?qs(x):null,x!==null&&(b=oi(x),x!==b||x.tag!==5&&x.tag!==6)&&(x=null)):(v=null,x=p),v!==x)){if(h=Hb,T="onMouseLeave",y="onMouseEnter",m="mouse",(e==="pointerout"||e==="pointerover")&&(h=Kb,T="onPointerLeave",y="onPointerEnter",m="pointer"),b=v==null?f:da(v),g=x==null?f:da(x),f=new h(T,m+"leave",v,r,c),f.target=b,f.relatedTarget=g,T=null,qs(c)===p&&(h=new h(y,m+"enter",x,r,c),h.target=g,h.relatedTarget=b,T=h),b=T,v&&x)t:{for(h=v,y=x,m=0,g=h;g;g=ia(g))m++;for(g=0,T=y;T;T=ia(T))g++;for(;0<m-g;)h=ia(h),m--;for(;0<g-m;)y=ia(y),g--;for(;m--;){if(h===y||y!==null&&h===y.alternate)break t;h=ia(h),y=ia(y)}h=null}else h=null;v!==null&&s0(u,f,v,h,!1),x!==null&&b!==null&&s0(u,b,x,h,!0)}}e:{if(f=p?da(p):window,v=f.nodeName&&f.nodeName.toLowerCase(),v==="select"||v==="input"&&f.type==="file")var w=w2;else if(Xb(f))if(TP)w=S2;else{w=R2;var $=_2}else(v=f.nodeName)&&v.toLowerCase()==="input"&&(f.type==="checkbox"||f.type==="radio")&&(w=E2);if(w&&(w=w(e,p))){xP(u,w,r,c);break e}$&&$(e,f,p),e==="focusout"&&($=f._wrapperState)&&$.controlled&&f.type==="number"&&oh(f,"number",f.value)}switch($=p?da(p):window,e){case"focusin":(Xb($)||$.contentEditable==="true")&&(ca=$,yh=p,vp=null);break;case"focusout":vp=yh=ca=null;break;case"mousedown":hh=!0;break;case"contextmenu":case"mouseup":case"dragend":hh=!1,e0(u,r,c);break;case"selectionchange":if(N2)break;case"keydown":case"keyup":e0(u,r,c)}var C;if(rg)e:{switch(e){case"compositionstart":var _="onCompositionStart";break e;case"compositionend":_="onCompositionEnd";break e;case"compositionupdate":_="onCompositionUpdate";break e}_=void 0}else pa?gP(e,r)&&(_="onCompositionEnd"):e==="keydown"&&r.keyCode===229&&(_="onCompositionStart");_&&(hP&&r.locale!=="ko"&&(pa||_!=="onCompositionStart"?_==="onCompositionEnd"&&pa&&(C=yP()):(os=c,Jh="value"in os?os.value:os.textContent,pa=!0)),$=Gu(p,_),0<$.length&&(_=new qb(_,e,null,r,c),u.push({event:_,listeners:$}),C?_.data=C:(C=vP(r),C!==null&&(_.data=C)))),(C=T2?b2(e,r):P2(e,r))&&(p=Gu(p,"onBeforeInput"),0<p.length&&(c=new qb("onBeforeInput","beforeinput",null,r,c),u.push({event:c,listeners:p}),c.data=C))}kP(u,t)})}function Np(e,t,r){return{instance:e,listener:t,currentTarget:r}}function Gu(e,t){for(var r=t+"Capture",o=[];e!==null;){var n=e,s=n.stateNode;n.tag===5&&s!==null&&(n=s,s=wp(e,r),s!=null&&o.unshift(Np(e,s,n)),s=wp(e,t),s!=null&&o.push(Np(e,s,n))),e=e.return}return o}function ia(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5);return e||null}function s0(e,t,r,o,n){for(var s=t._reactName,i=[];r!==null&&r!==o;){var a=r,l=a.alternate,p=a.stateNode;if(l!==null&&l===o)break;a.tag===5&&p!==null&&(a=p,n?(l=wp(r,s),l!=null&&i.unshift(Np(r,l,a))):n||(l=wp(r,s),l!=null&&i.push(Np(r,l,a)))),r=r.return}i.length!==0&&e.push({event:t,listeners:i})}var I2=/\r\n?/g,j2=/\u0000|\uFFFD/g;function i0(e){return(typeof e=="string"?e:""+e).replace(I2,`
`).replace(j2,"")}function wu(e,t,r){if(t=i0(t),i0(e)!==t&&r)throw Error(ee(425))}function Yu(){}var gh=null,vh=null;function xh(e,t){return e==="textarea"||e==="noscript"||typeof t.children=="string"||typeof t.children=="number"||typeof t.dangerouslySetInnerHTML=="object"&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Th=typeof setTimeout=="function"?setTimeout:void 0,D2=typeof clearTimeout=="function"?clearTimeout:void 0,a0=typeof Promise=="function"?Promise:void 0,L2=typeof queueMicrotask=="function"?queueMicrotask:typeof a0<"u"?function(e){return a0.resolve(null).then(e).catch(A2)}:Th;function A2(e){setTimeout(function(){throw e})}function By(e,t){var r=t,o=0;do{var n=r.nextSibling;if(e.removeChild(r),n&&n.nodeType===8)if(r=n.data,r==="/$"){if(o===0){e.removeChild(n),Ep(t);return}o--}else r!=="$"&&r!=="$?"&&r!=="$!"||o++;r=n}while(r);Ep(t)}function ls(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t==="$"||t==="$!"||t==="$?")break;if(t==="/$")return null}}return e}function l0(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var r=e.data;if(r==="$"||r==="$!"||r==="$?"){if(t===0)return e;t--}else r==="/$"&&t++}e=e.previousSibling}return null}var Ma=Math.random().toString(36).slice(2),an="__reactFiber$"+Ma,Mp="__reactProps$"+Ma,_n="__reactContainer$"+Ma,bh="__reactEvents$"+Ma,z2="__reactListeners$"+Ma,B2="__reactHandles$"+Ma;function qs(e){var t=e[an];if(t)return t;for(var r=e.parentNode;r;){if(t=r[_n]||r[an]){if(r=t.alternate,t.child!==null||r!==null&&r.child!==null)for(e=l0(e);e!==null;){if(r=e[an])return r;e=l0(e)}return t}e=r,r=e.parentNode}return null}function Up(e){return e=e[an]||e[_n],!e||e.tag!==5&&e.tag!==6&&e.tag!==13&&e.tag!==3?null:e}function da(e){if(e.tag===5||e.tag===6)return e.stateNode;throw Error(ee(33))}function yd(e){return e[Mp]||null}var Ph=[],fa=-1;function hs(e){return{current:e}}function Ye(e){0>fa||(e.current=Ph[fa],Ph[fa]=null,fa--)}function He(e,t){fa++,Ph[fa]=e.current,e.current=t}var ms={},lr=hs(ms),Ir=hs(!1),Qs=ms;function _a(e,t){var r=e.type.contextTypes;if(!r)return ms;var o=e.stateNode;if(o&&o.__reactInternalMemoizedUnmaskedChildContext===t)return o.__reactInternalMemoizedMaskedChildContext;var n={},s;for(s in r)n[s]=t[s];return o&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=t,e.__reactInternalMemoizedMaskedChildContext=n),n}function jr(e){return e=e.childContextTypes,e!=null}function Xu(){Ye(Ir),Ye(lr)}function p0(e,t,r){if(lr.current!==ms)throw Error(ee(168));He(lr,t),He(Ir,r)}function NP(e,t,r){var o=e.stateNode;if(t=t.childContextTypes,typeof o.getChildContext!="function")return r;o=o.getChildContext();for(var n in o)if(!(n in t))throw Error(ee(108,_N(e)||"Unknown",n));return lt({},r,o)}function Qu(e){return e=(e=e.stateNode)&&e.__reactInternalMemoizedMergedChildContext||ms,Qs=lr.current,He(lr,e),He(Ir,Ir.current),!0}function c0(e,t,r){var o=e.stateNode;if(!o)throw Error(ee(169));r?(e=NP(e,t,Qs),o.__reactInternalMemoizedMergedChildContext=e,Ye(Ir),Ye(lr),He(lr,e)):Ye(Ir),He(Ir,r)}var bn=null,hd=!1,Fy=!1;function MP(e){bn===null?bn=[e]:bn.push(e)}function F2(e){hd=!0,MP(e)}function gs(){if(!Fy&&bn!==null){Fy=!0;var e=0,t=De;try{var r=bn;for(De=1;e<r.length;e++){var o=r[e];do o=o(!0);while(o!==null)}bn=null,hd=!1}catch(n){throw bn!==null&&(bn=bn.slice(e+1)),nP(Yh,gs),n}finally{De=t,Fy=!1}}return null}var ma=[],ya=0,Zu=null,Ju=0,ao=[],lo=0,Zs=null,Pn=1,Cn="";function Vs(e,t){ma[ya++]=Ju,ma[ya++]=Zu,Zu=e,Ju=t}function IP(e,t,r){ao[lo++]=Pn,ao[lo++]=Cn,ao[lo++]=Zs,Zs=e;var o=Pn;e=Cn;var n=32-Fo(o)-1;o&=~(1<<n),r+=1;var s=32-Fo(t)+n;if(30<s){var i=n-n%5;s=(o&(1<<i)-1).toString(32),o>>=i,n-=i,Pn=1<<32-Fo(t)+n|r<<n|o,Cn=s+e}else Pn=1<<s|r<<n|o,Cn=e}function ng(e){e.return!==null&&(Vs(e,1),IP(e,1,0))}function sg(e){for(;e===Zu;)Zu=ma[--ya],ma[ya]=null,Ju=ma[--ya],ma[ya]=null;for(;e===Zs;)Zs=ao[--lo],ao[lo]=null,Cn=ao[--lo],ao[lo]=null,Pn=ao[--lo],ao[lo]=null}var Yr=null,Gr=null,tt=!1,Bo=null;function jP(e,t){var r=po(5,null,null,0);r.elementType="DELETED",r.stateNode=t,r.return=e,t=e.deletions,t===null?(e.deletions=[r],e.flags|=16):t.push(r)}function u0(e,t){switch(e.tag){case 5:var r=e.type;return t=t.nodeType!==1||r.toLowerCase()!==t.nodeName.toLowerCase()?null:t,t!==null?(e.stateNode=t,Yr=e,Gr=ls(t.firstChild),!0):!1;case 6:return t=e.pendingProps===""||t.nodeType!==3?null:t,t!==null?(e.stateNode=t,Yr=e,Gr=null,!0):!1;case 13:return t=t.nodeType!==8?null:t,t!==null?(r=Zs!==null?{id:Pn,overflow:Cn}:null,e.memoizedState={dehydrated:t,treeContext:r,retryLane:1073741824},r=po(18,null,null,0),r.stateNode=t,r.return=e,e.child=r,Yr=e,Gr=null,!0):!1;default:return!1}}function Ch(e){return(e.mode&1)!==0&&(e.flags&128)===0}function $h(e){if(tt){var t=Gr;if(t){var r=t;if(!u0(e,t)){if(Ch(e))throw Error(ee(418));t=ls(r.nextSibling);var o=Yr;t&&u0(e,t)?jP(o,r):(e.flags=e.flags&-4097|2,tt=!1,Yr=e)}}else{if(Ch(e))throw Error(ee(418));e.flags=e.flags&-4097|2,tt=!1,Yr=e}}}function d0(e){for(e=e.return;e!==null&&e.tag!==5&&e.tag!==3&&e.tag!==13;)e=e.return;Yr=e}function _u(e){if(e!==Yr)return!1;if(!tt)return d0(e),tt=!0,!1;var t;if((t=e.tag!==3)&&!(t=e.tag!==5)&&(t=e.type,t=t!=="head"&&t!=="body"&&!xh(e.type,e.memoizedProps)),t&&(t=Gr)){if(Ch(e))throw DP(),Error(ee(418));for(;t;)jP(e,t),t=ls(t.nextSibling)}if(d0(e),e.tag===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(ee(317));e:{for(e=e.nextSibling,t=0;e;){if(e.nodeType===8){var r=e.data;if(r==="/$"){if(t===0){Gr=ls(e.nextSibling);break e}t--}else r!=="$"&&r!=="$!"&&r!=="$?"||t++}e=e.nextSibling}Gr=null}}else Gr=Yr?ls(e.stateNode.nextSibling):null;return!0}function DP(){for(var e=Gr;e;)e=ls(e.nextSibling)}function Ra(){Gr=Yr=null,tt=!1}function ig(e){Bo===null?Bo=[e]:Bo.push(e)}var U2=Sn.ReactCurrentBatchConfig;function ip(e,t,r){if(e=r.ref,e!==null&&typeof e!="function"&&typeof e!="object"){if(r._owner){if(r=r._owner,r){if(r.tag!==1)throw Error(ee(309));var o=r.stateNode}if(!o)throw Error(ee(147,e));var n=o,s=""+e;return t!==null&&t.ref!==null&&typeof t.ref=="function"&&t.ref._stringRef===s?t.ref:(t=function(i){var a=n.refs;i===null?delete a[s]:a[s]=i},t._stringRef=s,t)}if(typeof e!="string")throw Error(ee(284));if(!r._owner)throw Error(ee(290,e))}return e}function Ru(e,t){throw e=Object.prototype.toString.call(t),Error(ee(31,e==="[object Object]"?"object with keys {"+Object.keys(t).join(", ")+"}":e))}function f0(e){var t=e._init;return t(e._payload)}function LP(e){function t(y,m){if(e){var g=y.deletions;g===null?(y.deletions=[m],y.flags|=16):g.push(m)}}function r(y,m){if(!e)return null;for(;m!==null;)t(y,m),m=m.sibling;return null}function o(y,m){for(y=new Map;m!==null;)m.key!==null?y.set(m.key,m):y.set(m.index,m),m=m.sibling;return y}function n(y,m){return y=ds(y,m),y.index=0,y.sibling=null,y}function s(y,m,g){return y.index=g,e?(g=y.alternate,g!==null?(g=g.index,g<m?(y.flags|=2,m):g):(y.flags|=2,m)):(y.flags|=1048576,m)}function i(y){return e&&y.alternate===null&&(y.flags|=2),y}function a(y,m,g,T){return m===null||m.tag!==6?(m=Gy(g,y.mode,T),m.return=y,m):(m=n(m,g),m.return=y,m)}function l(y,m,g,T){var w=g.type;return w===la?c(y,m,g.props.children,T,g.key):m!==null&&(m.elementType===w||typeof w=="object"&&w!==null&&w.$$typeof===Jn&&f0(w)===m.type)?(T=n(m,g.props),T.ref=ip(y,m,g),T.return=y,T):(T=Bu(g.type,g.key,g.props,null,y.mode,T),T.ref=ip(y,m,g),T.return=y,T)}function p(y,m,g,T){return m===null||m.tag!==4||m.stateNode.containerInfo!==g.containerInfo||m.stateNode.implementation!==g.implementation?(m=Yy(g,y.mode,T),m.return=y,m):(m=n(m,g.children||[]),m.return=y,m)}function c(y,m,g,T,w){return m===null||m.tag!==7?(m=Xs(g,y.mode,T,w),m.return=y,m):(m=n(m,g),m.return=y,m)}function u(y,m,g){if(typeof m=="string"&&m!==""||typeof m=="number")return m=Gy(""+m,y.mode,g),m.return=y,m;if(typeof m=="object"&&m!==null){switch(m.$$typeof){case du:return g=Bu(m.type,m.key,m.props,null,y.mode,g),g.ref=ip(y,null,m),g.return=y,g;case aa:return m=Yy(m,y.mode,g),m.return=y,m;case Jn:var T=m._init;return u(y,T(m._payload),g)}if(up(m)||rp(m))return m=Xs(m,y.mode,g,null),m.return=y,m;Ru(y,m)}return null}function f(y,m,g,T){var w=m!==null?m.key:null;if(typeof g=="string"&&g!==""||typeof g=="number")return w!==null?null:a(y,m,""+g,T);if(typeof g=="object"&&g!==null){switch(g.$$typeof){case du:return g.key===w?l(y,m,g,T):null;case aa:return g.key===w?p(y,m,g,T):null;case Jn:return w=g._init,f(y,m,w(g._payload),T)}if(up(g)||rp(g))return w!==null?null:c(y,m,g,T,null);Ru(y,g)}return null}function v(y,m,g,T,w){if(typeof T=="string"&&T!==""||typeof T=="number")return y=y.get(g)||null,a(m,y,""+T,w);if(typeof T=="object"&&T!==null){switch(T.$$typeof){case du:return y=y.get(T.key===null?g:T.key)||null,l(m,y,T,w);case aa:return y=y.get(T.key===null?g:T.key)||null,p(m,y,T,w);case Jn:var $=T._init;return v(y,m,g,$(T._payload),w)}if(up(T)||rp(T))return y=y.get(g)||null,c(m,y,T,w,null);Ru(m,T)}return null}function x(y,m,g,T){for(var w=null,$=null,C=m,_=m=0,S=null;C!==null&&_<g.length;_++){C.index>_?(S=C,C=null):S=C.sibling;var R=f(y,C,g[_],T);if(R===null){C===null&&(C=S);break}e&&C&&R.alternate===null&&t(y,C),m=s(R,m,_),$===null?w=R:$.sibling=R,$=R,C=S}if(_===g.length)return r(y,C),tt&&Vs(y,_),w;if(C===null){for(;_<g.length;_++)C=u(y,g[_],T),C!==null&&(m=s(C,m,_),$===null?w=C:$.sibling=C,$=C);return tt&&Vs(y,_),w}for(C=o(y,C);_<g.length;_++)S=v(C,y,_,g[_],T),S!==null&&(e&&S.alternate!==null&&C.delete(S.key===null?_:S.key),m=s(S,m,_),$===null?w=S:$.sibling=S,$=S);return e&&C.forEach(function(j){return t(y,j)}),tt&&Vs(y,_),w}function h(y,m,g,T){var w=rp(g);if(typeof w!="function")throw Error(ee(150));if(g=w.call(g),g==null)throw Error(ee(151));for(var $=w=null,C=m,_=m=0,S=null,R=g.next();C!==null&&!R.done;_++,R=g.next()){C.index>_?(S=C,C=null):S=C.sibling;var j=f(y,C,R.value,T);if(j===null){C===null&&(C=S);break}e&&C&&j.alternate===null&&t(y,C),m=s(j,m,_),$===null?w=j:$.sibling=j,$=j,C=S}if(R.done)return r(y,C),tt&&Vs(y,_),w;if(C===null){for(;!R.done;_++,R=g.next())R=u(y,R.value,T),R!==null&&(m=s(R,m,_),$===null?w=R:$.sibling=R,$=R);return tt&&Vs(y,_),w}for(C=o(y,C);!R.done;_++,R=g.next())R=v(C,y,_,R.value,T),R!==null&&(e&&R.alternate!==null&&C.delete(R.key===null?_:R.key),m=s(R,m,_),$===null?w=R:$.sibling=R,$=R);return e&&C.forEach(function(U){return t(y,U)}),tt&&Vs(y,_),w}function b(y,m,g,T){if(typeof g=="object"&&g!==null&&g.type===la&&g.key===null&&(g=g.props.children),typeof g=="object"&&g!==null){switch(g.$$typeof){case du:e:{for(var w=g.key,$=m;$!==null;){if($.key===w){if(w=g.type,w===la){if($.tag===7){r(y,$.sibling),m=n($,g.props.children),m.return=y,y=m;break e}}else if($.elementType===w||typeof w=="object"&&w!==null&&w.$$typeof===Jn&&f0(w)===$.type){r(y,$.sibling),m=n($,g.props),m.ref=ip(y,$,g),m.return=y,y=m;break e}r(y,$);break}else t(y,$);$=$.sibling}g.type===la?(m=Xs(g.props.children,y.mode,T,g.key),m.return=y,y=m):(T=Bu(g.type,g.key,g.props,null,y.mode,T),T.ref=ip(y,m,g),T.return=y,y=T)}return i(y);case aa:e:{for($=g.key;m!==null;){if(m.key===$)if(m.tag===4&&m.stateNode.containerInfo===g.containerInfo&&m.stateNode.implementation===g.implementation){r(y,m.sibling),m=n(m,g.children||[]),m.return=y,y=m;break e}else{r(y,m);break}else t(y,m);m=m.sibling}m=Yy(g,y.mode,T),m.return=y,y=m}return i(y);case Jn:return $=g._init,b(y,m,$(g._payload),T)}if(up(g))return x(y,m,g,T);if(rp(g))return h(y,m,g,T);Ru(y,g)}return typeof g=="string"&&g!==""||typeof g=="number"?(g=""+g,m!==null&&m.tag===6?(r(y,m.sibling),m=n(m,g),m.return=y,y=m):(r(y,m),m=Gy(g,y.mode,T),m.return=y,y=m),i(y)):r(y,m)}return b}var Ea=LP(!0),AP=LP(!1),ed=hs(null),td=null,ha=null,ag=null;function lg(){ag=ha=td=null}function pg(e){var t=ed.current;Ye(ed),e._currentValue=t}function wh(e,t,r){for(;e!==null;){var o=e.alternate;if((e.childLanes&t)!==t?(e.childLanes|=t,o!==null&&(o.childLanes|=t)):o!==null&&(o.childLanes&t)!==t&&(o.childLanes|=t),e===r)break;e=e.return}}function Ca(e,t){td=e,ag=ha=null,e=e.dependencies,e!==null&&e.firstContext!==null&&((e.lanes&t)!==0&&(Mr=!0),e.firstContext=null)}function uo(e){var t=e._currentValue;if(ag!==e)if(e={context:e,memoizedValue:t,next:null},ha===null){if(td===null)throw Error(ee(308));ha=e,td.dependencies={lanes:0,firstContext:e}}else ha=ha.next=e;return t}var Ks=null;function cg(e){Ks===null?Ks=[e]:Ks.push(e)}function zP(e,t,r,o){var n=t.interleaved;return n===null?(r.next=r,cg(t)):(r.next=n.next,n.next=r),t.interleaved=r,Rn(e,o)}function Rn(e,t){e.lanes|=t;var r=e.alternate;for(r!==null&&(r.lanes|=t),r=e,e=e.return;e!==null;)e.childLanes|=t,r=e.alternate,r!==null&&(r.childLanes|=t),r=e,e=e.return;return r.tag===3?r.stateNode:null}var es=!1;function ug(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function BP(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,effects:e.effects})}function $n(e,t){return{eventTime:e,lane:t,tag:0,payload:null,callback:null,next:null}}function ps(e,t,r){var o=e.updateQueue;if(o===null)return null;if(o=o.shared,(_e&2)!==0){var n=o.pending;return n===null?t.next=t:(t.next=n.next,n.next=t),o.pending=t,Rn(e,r)}return n=o.interleaved,n===null?(t.next=t,cg(o)):(t.next=n.next,n.next=t),o.interleaved=t,Rn(e,r)}function Iu(e,t,r){if(t=t.updateQueue,t!==null&&(t=t.shared,(r&4194240)!==0)){var o=t.lanes;o&=e.pendingLanes,r|=o,t.lanes=r,Xh(e,r)}}function m0(e,t){var r=e.updateQueue,o=e.alternate;if(o!==null&&(o=o.updateQueue,r===o)){var n=null,s=null;if(r=r.firstBaseUpdate,r!==null){do{var i={eventTime:r.eventTime,lane:r.lane,tag:r.tag,payload:r.payload,callback:r.callback,next:null};s===null?n=s=i:s=s.next=i,r=r.next}while(r!==null);s===null?n=s=t:s=s.next=t}else n=s=t;r={baseState:o.baseState,firstBaseUpdate:n,lastBaseUpdate:s,shared:o.shared,effects:o.effects},e.updateQueue=r;return}e=r.lastBaseUpdate,e===null?r.firstBaseUpdate=t:e.next=t,r.lastBaseUpdate=t}function rd(e,t,r,o){var n=e.updateQueue;es=!1;var s=n.firstBaseUpdate,i=n.lastBaseUpdate,a=n.shared.pending;if(a!==null){n.shared.pending=null;var l=a,p=l.next;l.next=null,i===null?s=p:i.next=p,i=l;var c=e.alternate;c!==null&&(c=c.updateQueue,a=c.lastBaseUpdate,a!==i&&(a===null?c.firstBaseUpdate=p:a.next=p,c.lastBaseUpdate=l))}if(s!==null){var u=n.baseState;i=0,c=p=l=null,a=s;do{var f=a.lane,v=a.eventTime;if((o&f)===f){c!==null&&(c=c.next={eventTime:v,lane:0,tag:a.tag,payload:a.payload,callback:a.callback,next:null});e:{var x=e,h=a;switch(f=t,v=r,h.tag){case 1:if(x=h.payload,typeof x=="function"){u=x.call(v,u,f);break e}u=x;break e;case 3:x.flags=x.flags&-65537|128;case 0:if(x=h.payload,f=typeof x=="function"?x.call(v,u,f):x,f==null)break e;u=lt({},u,f);break e;case 2:es=!0}}a.callback!==null&&a.lane!==0&&(e.flags|=64,f=n.effects,f===null?n.effects=[a]:f.push(a))}else v={eventTime:v,lane:f,tag:a.tag,payload:a.payload,callback:a.callback,next:null},c===null?(p=c=v,l=u):c=c.next=v,i|=f;if(a=a.next,a===null){if(a=n.shared.pending,a===null)break;f=a,a=f.next,f.next=null,n.lastBaseUpdate=f,n.shared.pending=null}}while(!0);if(c===null&&(l=u),n.baseState=l,n.firstBaseUpdate=p,n.lastBaseUpdate=c,t=n.shared.interleaved,t!==null){n=t;do i|=n.lane,n=n.next;while(n!==t)}else s===null&&(n.shared.lanes=0);ei|=i,e.lanes=i,e.memoizedState=u}}function y0(e,t,r){if(e=t.effects,t.effects=null,e!==null)for(t=0;t<e.length;t++){var o=e[t],n=o.callback;if(n!==null){if(o.callback=null,o=r,typeof n!="function")throw Error(ee(191,n));n.call(o)}}}var Wp={},pn=hs(Wp),Ip=hs(Wp),jp=hs(Wp);function Gs(e){if(e===Wp)throw Error(ee(174));return e}function dg(e,t){switch(He(jp,t),He(Ip,e),He(pn,Wp),e=t.nodeType,e){case 9:case 11:t=(t=t.documentElement)?t.namespaceURI:sh(null,"");break;default:e=e===8?t.parentNode:t,t=e.namespaceURI||null,e=e.tagName,t=sh(t,e)}Ye(pn),He(pn,t)}function Sa(){Ye(pn),Ye(Ip),Ye(jp)}function FP(e){Gs(jp.current);var t=Gs(pn.current),r=sh(t,e.type);t!==r&&(He(Ip,e),He(pn,r))}function fg(e){Ip.current===e&&(Ye(pn),Ye(Ip))}var it=hs(0);function od(e){for(var t=e;t!==null;){if(t.tag===13){var r=t.memoizedState;if(r!==null&&(r=r.dehydrated,r===null||r.data==="$?"||r.data==="$!"))return t}else if(t.tag===19&&t.memoizedProps.revealOrder!==void 0){if((t.flags&128)!==0)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var Uy=[];function mg(){for(var e=0;e<Uy.length;e++)Uy[e]._workInProgressVersionPrimary=null;Uy.length=0}var ju=Sn.ReactCurrentDispatcher,Wy=Sn.ReactCurrentBatchConfig,Js=0,at=null,kt=null,zt=null,nd=!1,xp=!1,Dp=0,W2=0;function sr(){throw Error(ee(321))}function yg(e,t){if(t===null)return!1;for(var r=0;r<t.length&&r<e.length;r++)if(!Wo(e[r],t[r]))return!1;return!0}function hg(e,t,r,o,n,s){if(Js=s,at=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,ju.current=e===null||e.memoizedState===null?K2:G2,e=r(o,n),xp){s=0;do{if(xp=!1,Dp=0,25<=s)throw Error(ee(301));s+=1,zt=kt=null,t.updateQueue=null,ju.current=Y2,e=r(o,n)}while(xp)}if(ju.current=sd,t=kt!==null&&kt.next!==null,Js=0,zt=kt=at=null,nd=!1,t)throw Error(ee(300));return e}function gg(){var e=Dp!==0;return Dp=0,e}function sn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return zt===null?at.memoizedState=zt=e:zt=zt.next=e,zt}function fo(){if(kt===null){var e=at.alternate;e=e!==null?e.memoizedState:null}else e=kt.next;var t=zt===null?at.memoizedState:zt.next;if(t!==null)zt=t,kt=e;else{if(e===null)throw Error(ee(310));kt=e,e={memoizedState:kt.memoizedState,baseState:kt.baseState,baseQueue:kt.baseQueue,queue:kt.queue,next:null},zt===null?at.memoizedState=zt=e:zt=zt.next=e}return zt}function Lp(e,t){return typeof t=="function"?t(e):t}function Vy(e){var t=fo(),r=t.queue;if(r===null)throw Error(ee(311));r.lastRenderedReducer=e;var o=kt,n=o.baseQueue,s=r.pending;if(s!==null){if(n!==null){var i=n.next;n.next=s.next,s.next=i}o.baseQueue=n=s,r.pending=null}if(n!==null){s=n.next,o=o.baseState;var a=i=null,l=null,p=s;do{var c=p.lane;if((Js&c)===c)l!==null&&(l=l.next={lane:0,action:p.action,hasEagerState:p.hasEagerState,eagerState:p.eagerState,next:null}),o=p.hasEagerState?p.eagerState:e(o,p.action);else{var u={lane:c,action:p.action,hasEagerState:p.hasEagerState,eagerState:p.eagerState,next:null};l===null?(a=l=u,i=o):l=l.next=u,at.lanes|=c,ei|=c}p=p.next}while(p!==null&&p!==s);l===null?i=o:l.next=a,Wo(o,t.memoizedState)||(Mr=!0),t.memoizedState=o,t.baseState=i,t.baseQueue=l,r.lastRenderedState=o}if(e=r.interleaved,e!==null){n=e;do s=n.lane,at.lanes|=s,ei|=s,n=n.next;while(n!==e)}else n===null&&(r.lanes=0);return[t.memoizedState,r.dispatch]}function Hy(e){var t=fo(),r=t.queue;if(r===null)throw Error(ee(311));r.lastRenderedReducer=e;var o=r.dispatch,n=r.pending,s=t.memoizedState;if(n!==null){r.pending=null;var i=n=n.next;do s=e(s,i.action),i=i.next;while(i!==n);Wo(s,t.memoizedState)||(Mr=!0),t.memoizedState=s,t.baseQueue===null&&(t.baseState=s),r.lastRenderedState=s}return[s,o]}function UP(){}function WP(e,t){var r=at,o=fo(),n=t(),s=!Wo(o.memoizedState,n);if(s&&(o.memoizedState=n,Mr=!0),o=o.queue,vg(qP.bind(null,r,o,e),[e]),o.getSnapshot!==t||s||zt!==null&&zt.memoizedState.tag&1){if(r.flags|=2048,Ap(9,HP.bind(null,r,o,n,t),void 0,null),Bt===null)throw Error(ee(349));(Js&30)!==0||VP(r,t,n)}return n}function VP(e,t,r){e.flags|=16384,e={getSnapshot:t,value:r},t=at.updateQueue,t===null?(t={lastEffect:null,stores:null},at.updateQueue=t,t.stores=[e]):(r=t.stores,r===null?t.stores=[e]:r.push(e))}function HP(e,t,r,o){t.value=r,t.getSnapshot=o,KP(t)&&GP(e)}function qP(e,t,r){return r(function(){KP(t)&&GP(e)})}function KP(e){var t=e.getSnapshot;e=e.value;try{var r=t();return!Wo(e,r)}catch{return!0}}function GP(e){var t=Rn(e,1);t!==null&&Uo(t,e,1,-1)}function h0(e){var t=sn();return typeof e=="function"&&(e=e()),t.memoizedState=t.baseState=e,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:Lp,lastRenderedState:e},t.queue=e,e=e.dispatch=q2.bind(null,at,e),[t.memoizedState,e]}function Ap(e,t,r,o){return e={tag:e,create:t,destroy:r,deps:o,next:null},t=at.updateQueue,t===null?(t={lastEffect:null,stores:null},at.updateQueue=t,t.lastEffect=e.next=e):(r=t.lastEffect,r===null?t.lastEffect=e.next=e:(o=r.next,r.next=e,e.next=o,t.lastEffect=e)),e}function YP(){return fo().memoizedState}function Du(e,t,r,o){var n=sn();at.flags|=e,n.memoizedState=Ap(1|t,r,void 0,o===void 0?null:o)}function gd(e,t,r,o){var n=fo();o=o===void 0?null:o;var s=void 0;if(kt!==null){var i=kt.memoizedState;if(s=i.destroy,o!==null&&yg(o,i.deps)){n.memoizedState=Ap(t,r,s,o);return}}at.flags|=e,n.memoizedState=Ap(1|t,r,s,o)}function g0(e,t){return Du(8390656,8,e,t)}function vg(e,t){return gd(2048,8,e,t)}function XP(e,t){return gd(4,2,e,t)}function QP(e,t){return gd(4,4,e,t)}function ZP(e,t){if(typeof t=="function")return e=e(),t(e),function(){t(null)};if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function JP(e,t,r){return r=r!=null?r.concat([e]):null,gd(4,4,ZP.bind(null,t,e),r)}function xg(){}function e1(e,t){var r=fo();t=t===void 0?null:t;var o=r.memoizedState;return o!==null&&t!==null&&yg(t,o[1])?o[0]:(r.memoizedState=[e,t],e)}function t1(e,t){var r=fo();t=t===void 0?null:t;var o=r.memoizedState;return o!==null&&t!==null&&yg(t,o[1])?o[0]:(e=e(),r.memoizedState=[e,t],e)}function r1(e,t,r){return(Js&21)===0?(e.baseState&&(e.baseState=!1,Mr=!0),e.memoizedState=r):(Wo(r,t)||(r=aP(),at.lanes|=r,ei|=r,e.baseState=!0),t)}function V2(e,t){var r=De;De=r!==0&&4>r?r:4,e(!0);var o=Wy.transition;Wy.transition={};try{e(!1),t()}finally{De=r,Wy.transition=o}}function o1(){return fo().memoizedState}function H2(e,t,r){var o=us(e);if(r={lane:o,action:r,hasEagerState:!1,eagerState:null,next:null},n1(e))s1(t,r);else if(r=zP(e,t,r,o),r!==null){var n=xr();Uo(r,e,o,n),i1(r,t,o)}}function q2(e,t,r){var o=us(e),n={lane:o,action:r,hasEagerState:!1,eagerState:null,next:null};if(n1(e))s1(t,n);else{var s=e.alternate;if(e.lanes===0&&(s===null||s.lanes===0)&&(s=t.lastRenderedReducer,s!==null))try{var i=t.lastRenderedState,a=s(i,r);if(n.hasEagerState=!0,n.eagerState=a,Wo(a,i)){var l=t.interleaved;l===null?(n.next=n,cg(t)):(n.next=l.next,l.next=n),t.interleaved=n;return}}catch{}finally{}r=zP(e,t,n,o),r!==null&&(n=xr(),Uo(r,e,o,n),i1(r,t,o))}}function n1(e){var t=e.alternate;return e===at||t!==null&&t===at}function s1(e,t){xp=nd=!0;var r=e.pending;r===null?t.next=t:(t.next=r.next,r.next=t),e.pending=t}function i1(e,t,r){if((r&4194240)!==0){var o=t.lanes;o&=e.pendingLanes,r|=o,t.lanes=r,Xh(e,r)}}var sd={readContext:uo,useCallback:sr,useContext:sr,useEffect:sr,useImperativeHandle:sr,useInsertionEffect:sr,useLayoutEffect:sr,useMemo:sr,useReducer:sr,useRef:sr,useState:sr,useDebugValue:sr,useDeferredValue:sr,useTransition:sr,useMutableSource:sr,useSyncExternalStore:sr,useId:sr,unstable_isNewReconciler:!1},K2={readContext:uo,useCallback:function(e,t){return sn().memoizedState=[e,t===void 0?null:t],e},useContext:uo,useEffect:g0,useImperativeHandle:function(e,t,r){return r=r!=null?r.concat([e]):null,Du(4194308,4,ZP.bind(null,t,e),r)},useLayoutEffect:function(e,t){return Du(4194308,4,e,t)},useInsertionEffect:function(e,t){return Du(4,2,e,t)},useMemo:function(e,t){var r=sn();return t=t===void 0?null:t,e=e(),r.memoizedState=[e,t],e},useReducer:function(e,t,r){var o=sn();return t=r!==void 0?r(t):t,o.memoizedState=o.baseState=t,e={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:t},o.queue=e,e=e.dispatch=H2.bind(null,at,e),[o.memoizedState,e]},useRef:function(e){var t=sn();return e={current:e},t.memoizedState=e},useState:h0,useDebugValue:xg,useDeferredValue:function(e){return sn().memoizedState=e},useTransition:function(){var e=h0(!1),t=e[0];return e=V2.bind(null,e[1]),sn().memoizedState=e,[t,e]},useMutableSource:function(){},useSyncExternalStore:function(e,t,r){var o=at,n=sn();if(tt){if(r===void 0)throw Error(ee(407));r=r()}else{if(r=t(),Bt===null)throw Error(ee(349));(Js&30)!==0||VP(o,t,r)}n.memoizedState=r;var s={value:r,getSnapshot:t};return n.queue=s,g0(qP.bind(null,o,s,e),[e]),o.flags|=2048,Ap(9,HP.bind(null,o,s,r,t),void 0,null),r},useId:function(){var e=sn(),t=Bt.identifierPrefix;if(tt){var r=Cn,o=Pn;r=(o&~(1<<32-Fo(o)-1)).toString(32)+r,t=":"+t+"R"+r,r=Dp++,0<r&&(t+="H"+r.toString(32)),t+=":"}else r=W2++,t=":"+t+"r"+r.toString(32)+":";return e.memoizedState=t},unstable_isNewReconciler:!1},G2={readContext:uo,useCallback:e1,useContext:uo,useEffect:vg,useImperativeHandle:JP,useInsertionEffect:XP,useLayoutEffect:QP,useMemo:t1,useReducer:Vy,useRef:YP,useState:function(){return Vy(Lp)},useDebugValue:xg,useDeferredValue:function(e){var t=fo();return r1(t,kt.memoizedState,e)},useTransition:function(){var e=Vy(Lp)[0],t=fo().memoizedState;return[e,t]},useMutableSource:UP,useSyncExternalStore:WP,useId:o1,unstable_isNewReconciler:!1},Y2={readContext:uo,useCallback:e1,useContext:uo,useEffect:vg,useImperativeHandle:JP,useInsertionEffect:XP,useLayoutEffect:QP,useMemo:t1,useReducer:Hy,useRef:YP,useState:function(){return Hy(Lp)},useDebugValue:xg,useDeferredValue:function(e){var t=fo();return kt===null?t.memoizedState=e:r1(t,kt.memoizedState,e)},useTransition:function(){var e=Hy(Lp)[0],t=fo().memoizedState;return[e,t]},useMutableSource:UP,useSyncExternalStore:WP,useId:o1,unstable_isNewReconciler:!1};function Ao(e,t){if(e&&e.defaultProps){t=lt({},t),e=e.defaultProps;for(var r in e)t[r]===void 0&&(t[r]=e[r]);return t}return t}function _h(e,t,r,o){t=e.memoizedState,r=r(o,t),r=r==null?t:lt({},t,r),e.memoizedState=r,e.lanes===0&&(e.updateQueue.baseState=r)}var vd={isMounted:function(e){return(e=e._reactInternals)?oi(e)===e:!1},enqueueSetState:function(e,t,r){e=e._reactInternals;var o=xr(),n=us(e),s=$n(o,n);s.payload=t,r!=null&&(s.callback=r),t=ps(e,s,n),t!==null&&(Uo(t,e,n,o),Iu(t,e,n))},enqueueReplaceState:function(e,t,r){e=e._reactInternals;var o=xr(),n=us(e),s=$n(o,n);s.tag=1,s.payload=t,r!=null&&(s.callback=r),t=ps(e,s,n),t!==null&&(Uo(t,e,n,o),Iu(t,e,n))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var r=xr(),o=us(e),n=$n(r,o);n.tag=2,t!=null&&(n.callback=t),t=ps(e,n,o),t!==null&&(Uo(t,e,o,r),Iu(t,e,o))}};function v0(e,t,r,o,n,s,i){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(o,s,i):t.prototype&&t.prototype.isPureReactComponent?!kp(r,o)||!kp(n,s):!0}function a1(e,t,r){var o=!1,n=ms,s=t.contextType;return typeof s=="object"&&s!==null?s=uo(s):(n=jr(t)?Qs:lr.current,o=t.contextTypes,s=(o=o!=null)?_a(e,n):ms),t=new t(r,s),e.memoizedState=t.state!==null&&t.state!==void 0?t.state:null,t.updater=vd,e.stateNode=t,t._reactInternals=e,o&&(e=e.stateNode,e.__reactInternalMemoizedUnmaskedChildContext=n,e.__reactInternalMemoizedMaskedChildContext=s),t}function x0(e,t,r,o){e=t.state,typeof t.componentWillReceiveProps=="function"&&t.componentWillReceiveProps(r,o),typeof t.UNSAFE_componentWillReceiveProps=="function"&&t.UNSAFE_componentWillReceiveProps(r,o),t.state!==e&&vd.enqueueReplaceState(t,t.state,null)}function Rh(e,t,r,o){var n=e.stateNode;n.props=r,n.state=e.memoizedState,n.refs={},ug(e);var s=t.contextType;typeof s=="object"&&s!==null?n.context=uo(s):(s=jr(t)?Qs:lr.current,n.context=_a(e,s)),n.state=e.memoizedState,s=t.getDerivedStateFromProps,typeof s=="function"&&(_h(e,t,s,r),n.state=e.memoizedState),typeof t.getDerivedStateFromProps=="function"||typeof n.getSnapshotBeforeUpdate=="function"||typeof n.UNSAFE_componentWillMount!="function"&&typeof n.componentWillMount!="function"||(t=n.state,typeof n.componentWillMount=="function"&&n.componentWillMount(),typeof n.UNSAFE_componentWillMount=="function"&&n.UNSAFE_componentWillMount(),t!==n.state&&vd.enqueueReplaceState(n,n.state,null),rd(e,r,n,o),n.state=e.memoizedState),typeof n.componentDidMount=="function"&&(e.flags|=4194308)}function ka(e,t){try{var r="",o=t;do r+=wN(o),o=o.return;while(o);var n=r}catch(s){n=`
Error generating stack: `+s.message+`
`+s.stack}return{value:e,source:t,stack:n,digest:null}}function qy(e,t,r){return{value:e,source:null,stack:r??null,digest:t??null}}function Eh(e,t){try{console.error(t.value)}catch(r){setTimeout(function(){throw r})}}var X2=typeof WeakMap=="function"?WeakMap:Map;function l1(e,t,r){r=$n(-1,r),r.tag=3,r.payload={element:null};var o=t.value;return r.callback=function(){ad||(ad=!0,Ah=o),Eh(e,t)},r}function p1(e,t,r){r=$n(-1,r),r.tag=3;var o=e.type.getDerivedStateFromError;if(typeof o=="function"){var n=t.value;r.payload=function(){return o(n)},r.callback=function(){Eh(e,t)}}var s=e.stateNode;return s!==null&&typeof s.componentDidCatch=="function"&&(r.callback=function(){Eh(e,t),typeof o!="function"&&(cs===null?cs=new Set([this]):cs.add(this));var i=t.stack;this.componentDidCatch(t.value,{componentStack:i!==null?i:""})}),r}function T0(e,t,r){var o=e.pingCache;if(o===null){o=e.pingCache=new X2;var n=new Set;o.set(t,n)}else n=o.get(t),n===void 0&&(n=new Set,o.set(t,n));n.has(r)||(n.add(r),e=cM.bind(null,e,t,r),t.then(e,e))}function b0(e){do{var t;if((t=e.tag===13)&&(t=e.memoizedState,t=t!==null?t.dehydrated!==null:!0),t)return e;e=e.return}while(e!==null);return null}function P0(e,t,r,o,n){return(e.mode&1)===0?(e===t?e.flags|=65536:(e.flags|=128,r.flags|=131072,r.flags&=-52805,r.tag===1&&(r.alternate===null?r.tag=17:(t=$n(-1,1),t.tag=2,ps(r,t,1))),r.lanes|=1),e):(e.flags|=65536,e.lanes=n,e)}var Q2=Sn.ReactCurrentOwner,Mr=!1;function vr(e,t,r,o){t.child=e===null?AP(t,null,r,o):Ea(t,e.child,r,o)}function C0(e,t,r,o,n){r=r.render;var s=t.ref;return Ca(t,n),o=hg(e,t,r,o,s,n),r=gg(),e!==null&&!Mr?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~n,En(e,t,n)):(tt&&r&&ng(t),t.flags|=1,vr(e,t,o,n),t.child)}function $0(e,t,r,o,n){if(e===null){var s=r.type;return typeof s=="function"&&!Rg(s)&&s.defaultProps===void 0&&r.compare===null&&r.defaultProps===void 0?(t.tag=15,t.type=s,c1(e,t,s,o,n)):(e=Bu(r.type,null,o,t,t.mode,n),e.ref=t.ref,e.return=t,t.child=e)}if(s=e.child,(e.lanes&n)===0){var i=s.memoizedProps;if(r=r.compare,r=r!==null?r:kp,r(i,o)&&e.ref===t.ref)return En(e,t,n)}return t.flags|=1,e=ds(s,o),e.ref=t.ref,e.return=t,t.child=e}function c1(e,t,r,o,n){if(e!==null){var s=e.memoizedProps;if(kp(s,o)&&e.ref===t.ref)if(Mr=!1,t.pendingProps=o=s,(e.lanes&n)!==0)(e.flags&131072)!==0&&(Mr=!0);else return t.lanes=e.lanes,En(e,t,n)}return Sh(e,t,r,o,n)}function u1(e,t,r){var o=t.pendingProps,n=o.children,s=e!==null?e.memoizedState:null;if(o.mode==="hidden")if((t.mode&1)===0)t.memoizedState={baseLanes:0,cachePool:null,transitions:null},He(va,Kr),Kr|=r;else{if((r&1073741824)===0)return e=s!==null?s.baseLanes|r:r,t.lanes=t.childLanes=1073741824,t.memoizedState={baseLanes:e,cachePool:null,transitions:null},t.updateQueue=null,He(va,Kr),Kr|=e,null;t.memoizedState={baseLanes:0,cachePool:null,transitions:null},o=s!==null?s.baseLanes:r,He(va,Kr),Kr|=o}else s!==null?(o=s.baseLanes|r,t.memoizedState=null):o=r,He(va,Kr),Kr|=o;return vr(e,t,n,r),t.child}function d1(e,t){var r=t.ref;(e===null&&r!==null||e!==null&&e.ref!==r)&&(t.flags|=512,t.flags|=2097152)}function Sh(e,t,r,o,n){var s=jr(r)?Qs:lr.current;return s=_a(t,s),Ca(t,n),r=hg(e,t,r,o,s,n),o=gg(),e!==null&&!Mr?(t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~n,En(e,t,n)):(tt&&o&&ng(t),t.flags|=1,vr(e,t,r,n),t.child)}function w0(e,t,r,o,n){if(jr(r)){var s=!0;Qu(t)}else s=!1;if(Ca(t,n),t.stateNode===null)Lu(e,t),a1(t,r,o),Rh(t,r,o,n),o=!0;else if(e===null){var i=t.stateNode,a=t.memoizedProps;i.props=a;var l=i.context,p=r.contextType;typeof p=="object"&&p!==null?p=uo(p):(p=jr(r)?Qs:lr.current,p=_a(t,p));var c=r.getDerivedStateFromProps,u=typeof c=="function"||typeof i.getSnapshotBeforeUpdate=="function";u||typeof i.UNSAFE_componentWillReceiveProps!="function"&&typeof i.componentWillReceiveProps!="function"||(a!==o||l!==p)&&x0(t,i,o,p),es=!1;var f=t.memoizedState;i.state=f,rd(t,o,i,n),l=t.memoizedState,a!==o||f!==l||Ir.current||es?(typeof c=="function"&&(_h(t,r,c,o),l=t.memoizedState),(a=es||v0(t,r,a,o,f,l,p))?(u||typeof i.UNSAFE_componentWillMount!="function"&&typeof i.componentWillMount!="function"||(typeof i.componentWillMount=="function"&&i.componentWillMount(),typeof i.UNSAFE_componentWillMount=="function"&&i.UNSAFE_componentWillMount()),typeof i.componentDidMount=="function"&&(t.flags|=4194308)):(typeof i.componentDidMount=="function"&&(t.flags|=4194308),t.memoizedProps=o,t.memoizedState=l),i.props=o,i.state=l,i.context=p,o=a):(typeof i.componentDidMount=="function"&&(t.flags|=4194308),o=!1)}else{i=t.stateNode,BP(e,t),a=t.memoizedProps,p=t.type===t.elementType?a:Ao(t.type,a),i.props=p,u=t.pendingProps,f=i.context,l=r.contextType,typeof l=="object"&&l!==null?l=uo(l):(l=jr(r)?Qs:lr.current,l=_a(t,l));var v=r.getDerivedStateFromProps;(c=typeof v=="function"||typeof i.getSnapshotBeforeUpdate=="function")||typeof i.UNSAFE_componentWillReceiveProps!="function"&&typeof i.componentWillReceiveProps!="function"||(a!==u||f!==l)&&x0(t,i,o,l),es=!1,f=t.memoizedState,i.state=f,rd(t,o,i,n);var x=t.memoizedState;a!==u||f!==x||Ir.current||es?(typeof v=="function"&&(_h(t,r,v,o),x=t.memoizedState),(p=es||v0(t,r,p,o,f,x,l)||!1)?(c||typeof i.UNSAFE_componentWillUpdate!="function"&&typeof i.componentWillUpdate!="function"||(typeof i.componentWillUpdate=="function"&&i.componentWillUpdate(o,x,l),typeof i.UNSAFE_componentWillUpdate=="function"&&i.UNSAFE_componentWillUpdate(o,x,l)),typeof i.componentDidUpdate=="function"&&(t.flags|=4),typeof i.getSnapshotBeforeUpdate=="function"&&(t.flags|=1024)):(typeof i.componentDidUpdate!="function"||a===e.memoizedProps&&f===e.memoizedState||(t.flags|=4),typeof i.getSnapshotBeforeUpdate!="function"||a===e.memoizedProps&&f===e.memoizedState||(t.flags|=1024),t.memoizedProps=o,t.memoizedState=x),i.props=o,i.state=x,i.context=l,o=p):(typeof i.componentDidUpdate!="function"||a===e.memoizedProps&&f===e.memoizedState||(t.flags|=4),typeof i.getSnapshotBeforeUpdate!="function"||a===e.memoizedProps&&f===e.memoizedState||(t.flags|=1024),o=!1)}return kh(e,t,r,o,s,n)}function kh(e,t,r,o,n,s){d1(e,t);var i=(t.flags&128)!==0;if(!o&&!i)return n&&c0(t,r,!1),En(e,t,s);o=t.stateNode,Q2.current=t;var a=i&&typeof r.getDerivedStateFromError!="function"?null:o.render();return t.flags|=1,e!==null&&i?(t.child=Ea(t,e.child,null,s),t.child=Ea(t,null,a,s)):vr(e,t,a,s),t.memoizedState=o.state,n&&c0(t,r,!0),t.child}function f1(e){var t=e.stateNode;t.pendingContext?p0(e,t.pendingContext,t.pendingContext!==t.context):t.context&&p0(e,t.context,!1),dg(e,t.containerInfo)}function _0(e,t,r,o,n){return Ra(),ig(n),t.flags|=256,vr(e,t,r,o),t.child}var Oh={dehydrated:null,treeContext:null,retryLane:0};function Nh(e){return{baseLanes:e,cachePool:null,transitions:null}}function m1(e,t,r){var o=t.pendingProps,n=it.current,s=!1,i=(t.flags&128)!==0,a;if((a=i)||(a=e!==null&&e.memoizedState===null?!1:(n&2)!==0),a?(s=!0,t.flags&=-129):(e===null||e.memoizedState!==null)&&(n|=1),He(it,n&1),e===null)return $h(t),e=t.memoizedState,e!==null&&(e=e.dehydrated,e!==null)?((t.mode&1)===0?t.lanes=1:e.data==="$!"?t.lanes=8:t.lanes=1073741824,null):(i=o.children,e=o.fallback,s?(o=t.mode,s=t.child,i={mode:"hidden",children:i},(o&1)===0&&s!==null?(s.childLanes=0,s.pendingProps=i):s=bd(i,o,0,null),e=Xs(e,o,r,null),s.return=t,e.return=t,s.sibling=e,t.child=s,t.child.memoizedState=Nh(r),t.memoizedState=Oh,e):Tg(t,i));if(n=e.memoizedState,n!==null&&(a=n.dehydrated,a!==null))return Z2(e,t,i,o,a,n,r);if(s){s=o.fallback,i=t.mode,n=e.child,a=n.sibling;var l={mode:"hidden",children:o.children};return(i&1)===0&&t.child!==n?(o=t.child,o.childLanes=0,o.pendingProps=l,t.deletions=null):(o=ds(n,l),o.subtreeFlags=n.subtreeFlags&14680064),a!==null?s=ds(a,s):(s=Xs(s,i,r,null),s.flags|=2),s.return=t,o.return=t,o.sibling=s,t.child=o,o=s,s=t.child,i=e.child.memoizedState,i=i===null?Nh(r):{baseLanes:i.baseLanes|r,cachePool:null,transitions:i.transitions},s.memoizedState=i,s.childLanes=e.childLanes&~r,t.memoizedState=Oh,o}return s=e.child,e=s.sibling,o=ds(s,{mode:"visible",children:o.children}),(t.mode&1)===0&&(o.lanes=r),o.return=t,o.sibling=null,e!==null&&(r=t.deletions,r===null?(t.deletions=[e],t.flags|=16):r.push(e)),t.child=o,t.memoizedState=null,o}function Tg(e,t){return t=bd({mode:"visible",children:t},e.mode,0,null),t.return=e,e.child=t}function Eu(e,t,r,o){return o!==null&&ig(o),Ea(t,e.child,null,r),e=Tg(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function Z2(e,t,r,o,n,s,i){if(r)return t.flags&256?(t.flags&=-257,o=qy(Error(ee(422))),Eu(e,t,i,o)):t.memoizedState!==null?(t.child=e.child,t.flags|=128,null):(s=o.fallback,n=t.mode,o=bd({mode:"visible",children:o.children},n,0,null),s=Xs(s,n,i,null),s.flags|=2,o.return=t,s.return=t,o.sibling=s,t.child=o,(t.mode&1)!==0&&Ea(t,e.child,null,i),t.child.memoizedState=Nh(i),t.memoizedState=Oh,s);if((t.mode&1)===0)return Eu(e,t,i,null);if(n.data==="$!"){if(o=n.nextSibling&&n.nextSibling.dataset,o)var a=o.dgst;return o=a,s=Error(ee(419)),o=qy(s,o,void 0),Eu(e,t,i,o)}if(a=(i&e.childLanes)!==0,Mr||a){if(o=Bt,o!==null){switch(i&-i){case 4:n=2;break;case 16:n=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:n=32;break;case 536870912:n=268435456;break;default:n=0}n=(n&(o.suspendedLanes|i))!==0?0:n,n!==0&&n!==s.retryLane&&(s.retryLane=n,Rn(e,n),Uo(o,e,n,-1))}return _g(),o=qy(Error(ee(421))),Eu(e,t,i,o)}return n.data==="$?"?(t.flags|=128,t.child=e.child,t=uM.bind(null,e),n._reactRetry=t,null):(e=s.treeContext,Gr=ls(n.nextSibling),Yr=t,tt=!0,Bo=null,e!==null&&(ao[lo++]=Pn,ao[lo++]=Cn,ao[lo++]=Zs,Pn=e.id,Cn=e.overflow,Zs=t),t=Tg(t,o.children),t.flags|=4096,t)}function R0(e,t,r){e.lanes|=t;var o=e.alternate;o!==null&&(o.lanes|=t),wh(e.return,t,r)}function Ky(e,t,r,o,n){var s=e.memoizedState;s===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:o,tail:r,tailMode:n}:(s.isBackwards=t,s.rendering=null,s.renderingStartTime=0,s.last=o,s.tail=r,s.tailMode=n)}function y1(e,t,r){var o=t.pendingProps,n=o.revealOrder,s=o.tail;if(vr(e,t,o.children,r),o=it.current,(o&2)!==0)o=o&1|2,t.flags|=128;else{if(e!==null&&(e.flags&128)!==0)e:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&R0(e,r,t);else if(e.tag===19)R0(e,r,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break e;for(;e.sibling===null;){if(e.return===null||e.return===t)break e;e=e.return}e.sibling.return=e.return,e=e.sibling}o&=1}if(He(it,o),(t.mode&1)===0)t.memoizedState=null;else switch(n){case"forwards":for(r=t.child,n=null;r!==null;)e=r.alternate,e!==null&&od(e)===null&&(n=r),r=r.sibling;r=n,r===null?(n=t.child,t.child=null):(n=r.sibling,r.sibling=null),Ky(t,!1,n,r,s);break;case"backwards":for(r=null,n=t.child,t.child=null;n!==null;){if(e=n.alternate,e!==null&&od(e)===null){t.child=n;break}e=n.sibling,n.sibling=r,r=n,n=e}Ky(t,!0,r,null,s);break;case"together":Ky(t,!1,null,null,void 0);break;default:t.memoizedState=null}return t.child}function Lu(e,t){(t.mode&1)===0&&e!==null&&(e.alternate=null,t.alternate=null,t.flags|=2)}function En(e,t,r){if(e!==null&&(t.dependencies=e.dependencies),ei|=t.lanes,(r&t.childLanes)===0)return null;if(e!==null&&t.child!==e.child)throw Error(ee(153));if(t.child!==null){for(e=t.child,r=ds(e,e.pendingProps),t.child=r,r.return=t;e.sibling!==null;)e=e.sibling,r=r.sibling=ds(e,e.pendingProps),r.return=t;r.sibling=null}return t.child}function J2(e,t,r){switch(t.tag){case 3:f1(t),Ra();break;case 5:FP(t);break;case 1:jr(t.type)&&Qu(t);break;case 4:dg(t,t.stateNode.containerInfo);break;case 10:var o=t.type._context,n=t.memoizedProps.value;He(ed,o._currentValue),o._currentValue=n;break;case 13:if(o=t.memoizedState,o!==null)return o.dehydrated!==null?(He(it,it.current&1),t.flags|=128,null):(r&t.child.childLanes)!==0?m1(e,t,r):(He(it,it.current&1),e=En(e,t,r),e!==null?e.sibling:null);He(it,it.current&1);break;case 19:if(o=(r&t.childLanes)!==0,(e.flags&128)!==0){if(o)return y1(e,t,r);t.flags|=128}if(n=t.memoizedState,n!==null&&(n.rendering=null,n.tail=null,n.lastEffect=null),He(it,it.current),o)break;return null;case 22:case 23:return t.lanes=0,u1(e,t,r)}return En(e,t,r)}var h1,Mh,g1,v1;h1=function(e,t){for(var r=t.child;r!==null;){if(r.tag===5||r.tag===6)e.appendChild(r.stateNode);else if(r.tag!==4&&r.child!==null){r.child.return=r,r=r.child;continue}if(r===t)break;for(;r.sibling===null;){if(r.return===null||r.return===t)return;r=r.return}r.sibling.return=r.return,r=r.sibling}};Mh=function(){};g1=function(e,t,r,o){var n=e.memoizedProps;if(n!==o){e=t.stateNode,Gs(pn.current);var s=null;switch(r){case"input":n=th(e,n),o=th(e,o),s=[];break;case"select":n=lt({},n,{value:void 0}),o=lt({},o,{value:void 0}),s=[];break;case"textarea":n=nh(e,n),o=nh(e,o),s=[];break;default:typeof n.onClick!="function"&&typeof o.onClick=="function"&&(e.onclick=Yu)}ih(r,o);var i;r=null;for(p in n)if(!o.hasOwnProperty(p)&&n.hasOwnProperty(p)&&n[p]!=null)if(p==="style"){var a=n[p];for(i in a)a.hasOwnProperty(i)&&(r||(r={}),r[i]="")}else p!=="dangerouslySetInnerHTML"&&p!=="children"&&p!=="suppressContentEditableWarning"&&p!=="suppressHydrationWarning"&&p!=="autoFocus"&&(Cp.hasOwnProperty(p)?s||(s=[]):(s=s||[]).push(p,null));for(p in o){var l=o[p];if(a=n?.[p],o.hasOwnProperty(p)&&l!==a&&(l!=null||a!=null))if(p==="style")if(a){for(i in a)!a.hasOwnProperty(i)||l&&l.hasOwnProperty(i)||(r||(r={}),r[i]="");for(i in l)l.hasOwnProperty(i)&&a[i]!==l[i]&&(r||(r={}),r[i]=l[i])}else r||(s||(s=[]),s.push(p,r)),r=l;else p==="dangerouslySetInnerHTML"?(l=l?l.__html:void 0,a=a?a.__html:void 0,l!=null&&a!==l&&(s=s||[]).push(p,l)):p==="children"?typeof l!="string"&&typeof l!="number"||(s=s||[]).push(p,""+l):p!=="suppressContentEditableWarning"&&p!=="suppressHydrationWarning"&&(Cp.hasOwnProperty(p)?(l!=null&&p==="onScroll"&&Ge("scroll",e),s||a===l||(s=[])):(s=s||[]).push(p,l))}r&&(s=s||[]).push("style",r);var p=s;(t.updateQueue=p)&&(t.flags|=4)}};v1=function(e,t,r,o){r!==o&&(t.flags|=4)};function ap(e,t){if(!tt)switch(e.tailMode){case"hidden":t=e.tail;for(var r=null;t!==null;)t.alternate!==null&&(r=t),t=t.sibling;r===null?e.tail=null:r.sibling=null;break;case"collapsed":r=e.tail;for(var o=null;r!==null;)r.alternate!==null&&(o=r),r=r.sibling;o===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:o.sibling=null}}function ir(e){var t=e.alternate!==null&&e.alternate.child===e.child,r=0,o=0;if(t)for(var n=e.child;n!==null;)r|=n.lanes|n.childLanes,o|=n.subtreeFlags&14680064,o|=n.flags&14680064,n.return=e,n=n.sibling;else for(n=e.child;n!==null;)r|=n.lanes|n.childLanes,o|=n.subtreeFlags,o|=n.flags,n.return=e,n=n.sibling;return e.subtreeFlags|=o,e.childLanes=r,t}function eM(e,t,r){var o=t.pendingProps;switch(sg(t),t.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return ir(t),null;case 1:return jr(t.type)&&Xu(),ir(t),null;case 3:return o=t.stateNode,Sa(),Ye(Ir),Ye(lr),mg(),o.pendingContext&&(o.context=o.pendingContext,o.pendingContext=null),(e===null||e.child===null)&&(_u(t)?t.flags|=4:e===null||e.memoizedState.isDehydrated&&(t.flags&256)===0||(t.flags|=1024,Bo!==null&&(Fh(Bo),Bo=null))),Mh(e,t),ir(t),null;case 5:fg(t);var n=Gs(jp.current);if(r=t.type,e!==null&&t.stateNode!=null)g1(e,t,r,o,n),e.ref!==t.ref&&(t.flags|=512,t.flags|=2097152);else{if(!o){if(t.stateNode===null)throw Error(ee(166));return ir(t),null}if(e=Gs(pn.current),_u(t)){o=t.stateNode,r=t.type;var s=t.memoizedProps;switch(o[an]=t,o[Mp]=s,e=(t.mode&1)!==0,r){case"dialog":Ge("cancel",o),Ge("close",o);break;case"iframe":case"object":case"embed":Ge("load",o);break;case"video":case"audio":for(n=0;n<fp.length;n++)Ge(fp[n],o);break;case"source":Ge("error",o);break;case"img":case"image":case"link":Ge("error",o),Ge("load",o);break;case"details":Ge("toggle",o);break;case"input":jb(o,s),Ge("invalid",o);break;case"select":o._wrapperState={wasMultiple:!!s.multiple},Ge("invalid",o);break;case"textarea":Lb(o,s),Ge("invalid",o)}ih(r,s),n=null;for(var i in s)if(s.hasOwnProperty(i)){var a=s[i];i==="children"?typeof a=="string"?o.textContent!==a&&(s.suppressHydrationWarning!==!0&&wu(o.textContent,a,e),n=["children",a]):typeof a=="number"&&o.textContent!==""+a&&(s.suppressHydrationWarning!==!0&&wu(o.textContent,a,e),n=["children",""+a]):Cp.hasOwnProperty(i)&&a!=null&&i==="onScroll"&&Ge("scroll",o)}switch(r){case"input":fu(o),Db(o,s,!0);break;case"textarea":fu(o),Ab(o);break;case"select":case"option":break;default:typeof s.onClick=="function"&&(o.onclick=Yu)}o=n,t.updateQueue=o,o!==null&&(t.flags|=4)}else{i=n.nodeType===9?n:n.ownerDocument,e==="http://www.w3.org/1999/xhtml"&&(e=q0(r)),e==="http://www.w3.org/1999/xhtml"?r==="script"?(e=i.createElement("div"),e.innerHTML="<script><\/script>",e=e.removeChild(e.firstChild)):typeof o.is=="string"?e=i.createElement(r,{is:o.is}):(e=i.createElement(r),r==="select"&&(i=e,o.multiple?i.multiple=!0:o.size&&(i.size=o.size))):e=i.createElementNS(e,r),e[an]=t,e[Mp]=o,h1(e,t,!1,!1),t.stateNode=e;e:{switch(i=ah(r,o),r){case"dialog":Ge("cancel",e),Ge("close",e),n=o;break;case"iframe":case"object":case"embed":Ge("load",e),n=o;break;case"video":case"audio":for(n=0;n<fp.length;n++)Ge(fp[n],e);n=o;break;case"source":Ge("error",e),n=o;break;case"img":case"image":case"link":Ge("error",e),Ge("load",e),n=o;break;case"details":Ge("toggle",e),n=o;break;case"input":jb(e,o),n=th(e,o),Ge("invalid",e);break;case"option":n=o;break;case"select":e._wrapperState={wasMultiple:!!o.multiple},n=lt({},o,{value:void 0}),Ge("invalid",e);break;case"textarea":Lb(e,o),n=nh(e,o),Ge("invalid",e);break;default:n=o}ih(r,n),a=n;for(s in a)if(a.hasOwnProperty(s)){var l=a[s];s==="style"?Y0(e,l):s==="dangerouslySetInnerHTML"?(l=l?l.__html:void 0,l!=null&&K0(e,l)):s==="children"?typeof l=="string"?(r!=="textarea"||l!=="")&&$p(e,l):typeof l=="number"&&$p(e,""+l):s!=="suppressContentEditableWarning"&&s!=="suppressHydrationWarning"&&s!=="autoFocus"&&(Cp.hasOwnProperty(s)?l!=null&&s==="onScroll"&&Ge("scroll",e):l!=null&&Vh(e,s,l,i))}switch(r){case"input":fu(e),Db(e,o,!1);break;case"textarea":fu(e),Ab(e);break;case"option":o.value!=null&&e.setAttribute("value",""+fs(o.value));break;case"select":e.multiple=!!o.multiple,s=o.value,s!=null?xa(e,!!o.multiple,s,!1):o.defaultValue!=null&&xa(e,!!o.multiple,o.defaultValue,!0);break;default:typeof n.onClick=="function"&&(e.onclick=Yu)}switch(r){case"button":case"input":case"select":case"textarea":o=!!o.autoFocus;break e;case"img":o=!0;break e;default:o=!1}}o&&(t.flags|=4)}t.ref!==null&&(t.flags|=512,t.flags|=2097152)}return ir(t),null;case 6:if(e&&t.stateNode!=null)v1(e,t,e.memoizedProps,o);else{if(typeof o!="string"&&t.stateNode===null)throw Error(ee(166));if(r=Gs(jp.current),Gs(pn.current),_u(t)){if(o=t.stateNode,r=t.memoizedProps,o[an]=t,(s=o.nodeValue!==r)&&(e=Yr,e!==null))switch(e.tag){case 3:wu(o.nodeValue,r,(e.mode&1)!==0);break;case 5:e.memoizedProps.suppressHydrationWarning!==!0&&wu(o.nodeValue,r,(e.mode&1)!==0)}s&&(t.flags|=4)}else o=(r.nodeType===9?r:r.ownerDocument).createTextNode(o),o[an]=t,t.stateNode=o}return ir(t),null;case 13:if(Ye(it),o=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(tt&&Gr!==null&&(t.mode&1)!==0&&(t.flags&128)===0)DP(),Ra(),t.flags|=98560,s=!1;else if(s=_u(t),o!==null&&o.dehydrated!==null){if(e===null){if(!s)throw Error(ee(318));if(s=t.memoizedState,s=s!==null?s.dehydrated:null,!s)throw Error(ee(317));s[an]=t}else Ra(),(t.flags&128)===0&&(t.memoizedState=null),t.flags|=4;ir(t),s=!1}else Bo!==null&&(Fh(Bo),Bo=null),s=!0;if(!s)return t.flags&65536?t:null}return(t.flags&128)!==0?(t.lanes=r,t):(o=o!==null,o!==(e!==null&&e.memoizedState!==null)&&o&&(t.child.flags|=8192,(t.mode&1)!==0&&(e===null||(it.current&1)!==0?Ot===0&&(Ot=3):_g())),t.updateQueue!==null&&(t.flags|=4),ir(t),null);case 4:return Sa(),Mh(e,t),e===null&&Op(t.stateNode.containerInfo),ir(t),null;case 10:return pg(t.type._context),ir(t),null;case 17:return jr(t.type)&&Xu(),ir(t),null;case 19:if(Ye(it),s=t.memoizedState,s===null)return ir(t),null;if(o=(t.flags&128)!==0,i=s.rendering,i===null)if(o)ap(s,!1);else{if(Ot!==0||e!==null&&(e.flags&128)!==0)for(e=t.child;e!==null;){if(i=od(e),i!==null){for(t.flags|=128,ap(s,!1),o=i.updateQueue,o!==null&&(t.updateQueue=o,t.flags|=4),t.subtreeFlags=0,o=r,r=t.child;r!==null;)s=r,e=o,s.flags&=14680066,i=s.alternate,i===null?(s.childLanes=0,s.lanes=e,s.child=null,s.subtreeFlags=0,s.memoizedProps=null,s.memoizedState=null,s.updateQueue=null,s.dependencies=null,s.stateNode=null):(s.childLanes=i.childLanes,s.lanes=i.lanes,s.child=i.child,s.subtreeFlags=0,s.deletions=null,s.memoizedProps=i.memoizedProps,s.memoizedState=i.memoizedState,s.updateQueue=i.updateQueue,s.type=i.type,e=i.dependencies,s.dependencies=e===null?null:{lanes:e.lanes,firstContext:e.firstContext}),r=r.sibling;return He(it,it.current&1|2),t.child}e=e.sibling}s.tail!==null&&xt()>Oa&&(t.flags|=128,o=!0,ap(s,!1),t.lanes=4194304)}else{if(!o)if(e=od(i),e!==null){if(t.flags|=128,o=!0,r=e.updateQueue,r!==null&&(t.updateQueue=r,t.flags|=4),ap(s,!0),s.tail===null&&s.tailMode==="hidden"&&!i.alternate&&!tt)return ir(t),null}else 2*xt()-s.renderingStartTime>Oa&&r!==1073741824&&(t.flags|=128,o=!0,ap(s,!1),t.lanes=4194304);s.isBackwards?(i.sibling=t.child,t.child=i):(r=s.last,r!==null?r.sibling=i:t.child=i,s.last=i)}return s.tail!==null?(t=s.tail,s.rendering=t,s.tail=t.sibling,s.renderingStartTime=xt(),t.sibling=null,r=it.current,He(it,o?r&1|2:r&1),t):(ir(t),null);case 22:case 23:return wg(),o=t.memoizedState!==null,e!==null&&e.memoizedState!==null!==o&&(t.flags|=8192),o&&(t.mode&1)!==0?(Kr&1073741824)!==0&&(ir(t),t.subtreeFlags&6&&(t.flags|=8192)):ir(t),null;case 24:return null;case 25:return null}throw Error(ee(156,t.tag))}function tM(e,t){switch(sg(t),t.tag){case 1:return jr(t.type)&&Xu(),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return Sa(),Ye(Ir),Ye(lr),mg(),e=t.flags,(e&65536)!==0&&(e&128)===0?(t.flags=e&-65537|128,t):null;case 5:return fg(t),null;case 13:if(Ye(it),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(ee(340));Ra()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return Ye(it),null;case 4:return Sa(),null;case 10:return pg(t.type._context),null;case 22:case 23:return wg(),null;case 24:return null;default:return null}}var Su=!1,ar=!1,rM=typeof WeakSet=="function"?WeakSet:Set,oe=null;function ga(e,t){var r=e.ref;if(r!==null)if(typeof r=="function")try{r(null)}catch(o){mt(e,t,o)}else r.current=null}function Ih(e,t,r){try{r()}catch(o){mt(e,t,o)}}var E0=!1;function oM(e,t){if(gh=qu,e=CP(),og(e)){if("selectionStart"in e)var r={start:e.selectionStart,end:e.selectionEnd};else e:{r=(r=e.ownerDocument)&&r.defaultView||window;var o=r.getSelection&&r.getSelection();if(o&&o.rangeCount!==0){r=o.anchorNode;var n=o.anchorOffset,s=o.focusNode;o=o.focusOffset;try{r.nodeType,s.nodeType}catch{r=null;break e}var i=0,a=-1,l=-1,p=0,c=0,u=e,f=null;t:for(;;){for(var v;u!==r||n!==0&&u.nodeType!==3||(a=i+n),u!==s||o!==0&&u.nodeType!==3||(l=i+o),u.nodeType===3&&(i+=u.nodeValue.length),(v=u.firstChild)!==null;)f=u,u=v;for(;;){if(u===e)break t;if(f===r&&++p===n&&(a=i),f===s&&++c===o&&(l=i),(v=u.nextSibling)!==null)break;u=f,f=u.parentNode}u=v}r=a===-1||l===-1?null:{start:a,end:l}}else r=null}r=r||{start:0,end:0}}else r=null;for(vh={focusedElem:e,selectionRange:r},qu=!1,oe=t;oe!==null;)if(t=oe,e=t.child,(t.subtreeFlags&1028)!==0&&e!==null)e.return=t,oe=e;else for(;oe!==null;){t=oe;try{var x=t.alternate;if((t.flags&1024)!==0)switch(t.tag){case 0:case 11:case 15:break;case 1:if(x!==null){var h=x.memoizedProps,b=x.memoizedState,y=t.stateNode,m=y.getSnapshotBeforeUpdate(t.elementType===t.type?h:Ao(t.type,h),b);y.__reactInternalSnapshotBeforeUpdate=m}break;case 3:var g=t.stateNode.containerInfo;g.nodeType===1?g.textContent="":g.nodeType===9&&g.documentElement&&g.removeChild(g.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(ee(163))}}catch(T){mt(t,t.return,T)}if(e=t.sibling,e!==null){e.return=t.return,oe=e;break}oe=t.return}return x=E0,E0=!1,x}function Tp(e,t,r){var o=t.updateQueue;if(o=o!==null?o.lastEffect:null,o!==null){var n=o=o.next;do{if((n.tag&e)===e){var s=n.destroy;n.destroy=void 0,s!==void 0&&Ih(t,r,s)}n=n.next}while(n!==o)}}function xd(e,t){if(t=t.updateQueue,t=t!==null?t.lastEffect:null,t!==null){var r=t=t.next;do{if((r.tag&e)===e){var o=r.create;r.destroy=o()}r=r.next}while(r!==t)}}function jh(e){var t=e.ref;if(t!==null){var r=e.stateNode;switch(e.tag){case 5:e=r;break;default:e=r}typeof t=="function"?t(e):t.current=e}}function x1(e){var t=e.alternate;t!==null&&(e.alternate=null,x1(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&(delete t[an],delete t[Mp],delete t[bh],delete t[z2],delete t[B2])),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}function T1(e){return e.tag===5||e.tag===3||e.tag===4}function S0(e){e:for(;;){for(;e.sibling===null;){if(e.return===null||T1(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.flags&2||e.child===null||e.tag===4)continue e;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Dh(e,t,r){var o=e.tag;if(o===5||o===6)e=e.stateNode,t?r.nodeType===8?r.parentNode.insertBefore(e,t):r.insertBefore(e,t):(r.nodeType===8?(t=r.parentNode,t.insertBefore(e,r)):(t=r,t.appendChild(e)),r=r._reactRootContainer,r!=null||t.onclick!==null||(t.onclick=Yu));else if(o!==4&&(e=e.child,e!==null))for(Dh(e,t,r),e=e.sibling;e!==null;)Dh(e,t,r),e=e.sibling}function Lh(e,t,r){var o=e.tag;if(o===5||o===6)e=e.stateNode,t?r.insertBefore(e,t):r.appendChild(e);else if(o!==4&&(e=e.child,e!==null))for(Lh(e,t,r),e=e.sibling;e!==null;)Lh(e,t,r),e=e.sibling}var Xt=null,zo=!1;function Zn(e,t,r){for(r=r.child;r!==null;)b1(e,t,r),r=r.sibling}function b1(e,t,r){if(ln&&typeof ln.onCommitFiberUnmount=="function")try{ln.onCommitFiberUnmount(ud,r)}catch{}switch(r.tag){case 5:ar||ga(r,t);case 6:var o=Xt,n=zo;Xt=null,Zn(e,t,r),Xt=o,zo=n,Xt!==null&&(zo?(e=Xt,r=r.stateNode,e.nodeType===8?e.parentNode.removeChild(r):e.removeChild(r)):Xt.removeChild(r.stateNode));break;case 18:Xt!==null&&(zo?(e=Xt,r=r.stateNode,e.nodeType===8?By(e.parentNode,r):e.nodeType===1&&By(e,r),Ep(e)):By(Xt,r.stateNode));break;case 4:o=Xt,n=zo,Xt=r.stateNode.containerInfo,zo=!0,Zn(e,t,r),Xt=o,zo=n;break;case 0:case 11:case 14:case 15:if(!ar&&(o=r.updateQueue,o!==null&&(o=o.lastEffect,o!==null))){n=o=o.next;do{var s=n,i=s.destroy;s=s.tag,i!==void 0&&((s&2)!==0||(s&4)!==0)&&Ih(r,t,i),n=n.next}while(n!==o)}Zn(e,t,r);break;case 1:if(!ar&&(ga(r,t),o=r.stateNode,typeof o.componentWillUnmount=="function"))try{o.props=r.memoizedProps,o.state=r.memoizedState,o.componentWillUnmount()}catch(a){mt(r,t,a)}Zn(e,t,r);break;case 21:Zn(e,t,r);break;case 22:r.mode&1?(ar=(o=ar)||r.memoizedState!==null,Zn(e,t,r),ar=o):Zn(e,t,r);break;default:Zn(e,t,r)}}function k0(e){var t=e.updateQueue;if(t!==null){e.updateQueue=null;var r=e.stateNode;r===null&&(r=e.stateNode=new rM),t.forEach(function(o){var n=dM.bind(null,e,o);r.has(o)||(r.add(o),o.then(n,n))})}}function Lo(e,t){var r=t.deletions;if(r!==null)for(var o=0;o<r.length;o++){var n=r[o];try{var s=e,i=t,a=i;e:for(;a!==null;){switch(a.tag){case 5:Xt=a.stateNode,zo=!1;break e;case 3:Xt=a.stateNode.containerInfo,zo=!0;break e;case 4:Xt=a.stateNode.containerInfo,zo=!0;break e}a=a.return}if(Xt===null)throw Error(ee(160));b1(s,i,n),Xt=null,zo=!1;var l=n.alternate;l!==null&&(l.return=null),n.return=null}catch(p){mt(n,t,p)}}if(t.subtreeFlags&12854)for(t=t.child;t!==null;)P1(t,e),t=t.sibling}function P1(e,t){var r=e.alternate,o=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:if(Lo(t,e),nn(e),o&4){try{Tp(3,e,e.return),xd(3,e)}catch(h){mt(e,e.return,h)}try{Tp(5,e,e.return)}catch(h){mt(e,e.return,h)}}break;case 1:Lo(t,e),nn(e),o&512&&r!==null&&ga(r,r.return);break;case 5:if(Lo(t,e),nn(e),o&512&&r!==null&&ga(r,r.return),e.flags&32){var n=e.stateNode;try{$p(n,"")}catch(h){mt(e,e.return,h)}}if(o&4&&(n=e.stateNode,n!=null)){var s=e.memoizedProps,i=r!==null?r.memoizedProps:s,a=e.type,l=e.updateQueue;if(e.updateQueue=null,l!==null)try{a==="input"&&s.type==="radio"&&s.name!=null&&V0(n,s),ah(a,i);var p=ah(a,s);for(i=0;i<l.length;i+=2){var c=l[i],u=l[i+1];c==="style"?Y0(n,u):c==="dangerouslySetInnerHTML"?K0(n,u):c==="children"?$p(n,u):Vh(n,c,u,p)}switch(a){case"input":rh(n,s);break;case"textarea":H0(n,s);break;case"select":var f=n._wrapperState.wasMultiple;n._wrapperState.wasMultiple=!!s.multiple;var v=s.value;v!=null?xa(n,!!s.multiple,v,!1):f!==!!s.multiple&&(s.defaultValue!=null?xa(n,!!s.multiple,s.defaultValue,!0):xa(n,!!s.multiple,s.multiple?[]:"",!1))}n[Mp]=s}catch(h){mt(e,e.return,h)}}break;case 6:if(Lo(t,e),nn(e),o&4){if(e.stateNode===null)throw Error(ee(162));n=e.stateNode,s=e.memoizedProps;try{n.nodeValue=s}catch(h){mt(e,e.return,h)}}break;case 3:if(Lo(t,e),nn(e),o&4&&r!==null&&r.memoizedState.isDehydrated)try{Ep(t.containerInfo)}catch(h){mt(e,e.return,h)}break;case 4:Lo(t,e),nn(e);break;case 13:Lo(t,e),nn(e),n=e.child,n.flags&8192&&(s=n.memoizedState!==null,n.stateNode.isHidden=s,!s||n.alternate!==null&&n.alternate.memoizedState!==null||(Cg=xt())),o&4&&k0(e);break;case 22:if(c=r!==null&&r.memoizedState!==null,e.mode&1?(ar=(p=ar)||c,Lo(t,e),ar=p):Lo(t,e),nn(e),o&8192){if(p=e.memoizedState!==null,(e.stateNode.isHidden=p)&&!c&&(e.mode&1)!==0)for(oe=e,c=e.child;c!==null;){for(u=oe=c;oe!==null;){switch(f=oe,v=f.child,f.tag){case 0:case 11:case 14:case 15:Tp(4,f,f.return);break;case 1:ga(f,f.return);var x=f.stateNode;if(typeof x.componentWillUnmount=="function"){o=f,r=f.return;try{t=o,x.props=t.memoizedProps,x.state=t.memoizedState,x.componentWillUnmount()}catch(h){mt(o,r,h)}}break;case 5:ga(f,f.return);break;case 22:if(f.memoizedState!==null){N0(u);continue}}v!==null?(v.return=f,oe=v):N0(u)}c=c.sibling}e:for(c=null,u=e;;){if(u.tag===5){if(c===null){c=u;try{n=u.stateNode,p?(s=n.style,typeof s.setProperty=="function"?s.setProperty("display","none","important"):s.display="none"):(a=u.stateNode,l=u.memoizedProps.style,i=l!=null&&l.hasOwnProperty("display")?l.display:null,a.style.display=G0("display",i))}catch(h){mt(e,e.return,h)}}}else if(u.tag===6){if(c===null)try{u.stateNode.nodeValue=p?"":u.memoizedProps}catch(h){mt(e,e.return,h)}}else if((u.tag!==22&&u.tag!==23||u.memoizedState===null||u===e)&&u.child!==null){u.child.return=u,u=u.child;continue}if(u===e)break e;for(;u.sibling===null;){if(u.return===null||u.return===e)break e;c===u&&(c=null),u=u.return}c===u&&(c=null),u.sibling.return=u.return,u=u.sibling}}break;case 19:Lo(t,e),nn(e),o&4&&k0(e);break;case 21:break;default:Lo(t,e),nn(e)}}function nn(e){var t=e.flags;if(t&2){try{e:{for(var r=e.return;r!==null;){if(T1(r)){var o=r;break e}r=r.return}throw Error(ee(160))}switch(o.tag){case 5:var n=o.stateNode;o.flags&32&&($p(n,""),o.flags&=-33);var s=S0(e);Lh(e,s,n);break;case 3:case 4:var i=o.stateNode.containerInfo,a=S0(e);Dh(e,a,i);break;default:throw Error(ee(161))}}catch(l){mt(e,e.return,l)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function nM(e,t,r){oe=e,C1(e,t,r)}function C1(e,t,r){for(var o=(e.mode&1)!==0;oe!==null;){var n=oe,s=n.child;if(n.tag===22&&o){var i=n.memoizedState!==null||Su;if(!i){var a=n.alternate,l=a!==null&&a.memoizedState!==null||ar;a=Su;var p=ar;if(Su=i,(ar=l)&&!p)for(oe=n;oe!==null;)i=oe,l=i.child,i.tag===22&&i.memoizedState!==null?M0(n):l!==null?(l.return=i,oe=l):M0(n);for(;s!==null;)oe=s,C1(s,t,r),s=s.sibling;oe=n,Su=a,ar=p}O0(e,t,r)}else(n.subtreeFlags&8772)!==0&&s!==null?(s.return=n,oe=s):O0(e,t,r)}}function O0(e){for(;oe!==null;){var t=oe;if((t.flags&8772)!==0){var r=t.alternate;try{if((t.flags&8772)!==0)switch(t.tag){case 0:case 11:case 15:ar||xd(5,t);break;case 1:var o=t.stateNode;if(t.flags&4&&!ar)if(r===null)o.componentDidMount();else{var n=t.elementType===t.type?r.memoizedProps:Ao(t.type,r.memoizedProps);o.componentDidUpdate(n,r.memoizedState,o.__reactInternalSnapshotBeforeUpdate)}var s=t.updateQueue;s!==null&&y0(t,s,o);break;case 3:var i=t.updateQueue;if(i!==null){if(r=null,t.child!==null)switch(t.child.tag){case 5:r=t.child.stateNode;break;case 1:r=t.child.stateNode}y0(t,i,r)}break;case 5:var a=t.stateNode;if(r===null&&t.flags&4){r=a;var l=t.memoizedProps;switch(t.type){case"button":case"input":case"select":case"textarea":l.autoFocus&&r.focus();break;case"img":l.src&&(r.src=l.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(t.memoizedState===null){var p=t.alternate;if(p!==null){var c=p.memoizedState;if(c!==null){var u=c.dehydrated;u!==null&&Ep(u)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(ee(163))}ar||t.flags&512&&jh(t)}catch(f){mt(t,t.return,f)}}if(t===e){oe=null;break}if(r=t.sibling,r!==null){r.return=t.return,oe=r;break}oe=t.return}}function N0(e){for(;oe!==null;){var t=oe;if(t===e){oe=null;break}var r=t.sibling;if(r!==null){r.return=t.return,oe=r;break}oe=t.return}}function M0(e){for(;oe!==null;){var t=oe;try{switch(t.tag){case 0:case 11:case 15:var r=t.return;try{xd(4,t)}catch(l){mt(t,r,l)}break;case 1:var o=t.stateNode;if(typeof o.componentDidMount=="function"){var n=t.return;try{o.componentDidMount()}catch(l){mt(t,n,l)}}var s=t.return;try{jh(t)}catch(l){mt(t,s,l)}break;case 5:var i=t.return;try{jh(t)}catch(l){mt(t,i,l)}}}catch(l){mt(t,t.return,l)}if(t===e){oe=null;break}var a=t.sibling;if(a!==null){a.return=t.return,oe=a;break}oe=t.return}}var sM=Math.ceil,id=Sn.ReactCurrentDispatcher,bg=Sn.ReactCurrentOwner,co=Sn.ReactCurrentBatchConfig,_e=0,Bt=null,Rt=null,Qt=0,Kr=0,va=hs(0),Ot=0,zp=null,ei=0,Td=0,Pg=0,bp=null,Nr=null,Cg=0,Oa=1/0,Tn=null,ad=!1,Ah=null,cs=null,ku=!1,ns=null,ld=0,Pp=0,zh=null,Au=-1,zu=0;function xr(){return(_e&6)!==0?xt():Au!==-1?Au:Au=xt()}function us(e){return(e.mode&1)===0?1:(_e&2)!==0&&Qt!==0?Qt&-Qt:U2.transition!==null?(zu===0&&(zu=aP()),zu):(e=De,e!==0||(e=window.event,e=e===void 0?16:mP(e.type)),e)}function Uo(e,t,r,o){if(50<Pp)throw Pp=0,zh=null,Error(ee(185));Bp(e,r,o),((_e&2)===0||e!==Bt)&&(e===Bt&&((_e&2)===0&&(Td|=r),Ot===4&&rs(e,Qt)),Dr(e,o),r===1&&_e===0&&(t.mode&1)===0&&(Oa=xt()+500,hd&&gs()))}function Dr(e,t){var r=e.callbackNode;VN(e,t);var o=Hu(e,e===Bt?Qt:0);if(o===0)r!==null&&Fb(r),e.callbackNode=null,e.callbackPriority=0;else if(t=o&-o,e.callbackPriority!==t){if(r!=null&&Fb(r),t===1)e.tag===0?F2(I0.bind(null,e)):MP(I0.bind(null,e)),L2(function(){(_e&6)===0&&gs()}),r=null;else{switch(lP(o)){case 1:r=Yh;break;case 4:r=sP;break;case 16:r=Vu;break;case 536870912:r=iP;break;default:r=Vu}r=O1(r,$1.bind(null,e))}e.callbackPriority=t,e.callbackNode=r}}function $1(e,t){if(Au=-1,zu=0,(_e&6)!==0)throw Error(ee(327));var r=e.callbackNode;if($a()&&e.callbackNode!==r)return null;var o=Hu(e,e===Bt?Qt:0);if(o===0)return null;if((o&30)!==0||(o&e.expiredLanes)!==0||t)t=pd(e,o);else{t=o;var n=_e;_e|=2;var s=_1();(Bt!==e||Qt!==t)&&(Tn=null,Oa=xt()+500,Ys(e,t));do try{lM();break}catch(a){w1(e,a)}while(!0);lg(),id.current=s,_e=n,Rt!==null?t=0:(Bt=null,Qt=0,t=Ot)}if(t!==0){if(t===2&&(n=dh(e),n!==0&&(o=n,t=Bh(e,n))),t===1)throw r=zp,Ys(e,0),rs(e,o),Dr(e,xt()),r;if(t===6)rs(e,o);else{if(n=e.current.alternate,(o&30)===0&&!iM(n)&&(t=pd(e,o),t===2&&(s=dh(e),s!==0&&(o=s,t=Bh(e,s))),t===1))throw r=zp,Ys(e,0),rs(e,o),Dr(e,xt()),r;switch(e.finishedWork=n,e.finishedLanes=o,t){case 0:case 1:throw Error(ee(345));case 2:Hs(e,Nr,Tn);break;case 3:if(rs(e,o),(o&130023424)===o&&(t=Cg+500-xt(),10<t)){if(Hu(e,0)!==0)break;if(n=e.suspendedLanes,(n&o)!==o){xr(),e.pingedLanes|=e.suspendedLanes&n;break}e.timeoutHandle=Th(Hs.bind(null,e,Nr,Tn),t);break}Hs(e,Nr,Tn);break;case 4:if(rs(e,o),(o&4194240)===o)break;for(t=e.eventTimes,n=-1;0<o;){var i=31-Fo(o);s=1<<i,i=t[i],i>n&&(n=i),o&=~s}if(o=n,o=xt()-o,o=(120>o?120:480>o?480:1080>o?1080:1920>o?1920:3e3>o?3e3:4320>o?4320:1960*sM(o/1960))-o,10<o){e.timeoutHandle=Th(Hs.bind(null,e,Nr,Tn),o);break}Hs(e,Nr,Tn);break;case 5:Hs(e,Nr,Tn);break;default:throw Error(ee(329))}}}return Dr(e,xt()),e.callbackNode===r?$1.bind(null,e):null}function Bh(e,t){var r=bp;return e.current.memoizedState.isDehydrated&&(Ys(e,t).flags|=256),e=pd(e,t),e!==2&&(t=Nr,Nr=r,t!==null&&Fh(t)),e}function Fh(e){Nr===null?Nr=e:Nr.push.apply(Nr,e)}function iM(e){for(var t=e;;){if(t.flags&16384){var r=t.updateQueue;if(r!==null&&(r=r.stores,r!==null))for(var o=0;o<r.length;o++){var n=r[o],s=n.getSnapshot;n=n.value;try{if(!Wo(s(),n))return!1}catch{return!1}}}if(r=t.child,t.subtreeFlags&16384&&r!==null)r.return=t,t=r;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function rs(e,t){for(t&=~Pg,t&=~Td,e.suspendedLanes|=t,e.pingedLanes&=~t,e=e.expirationTimes;0<t;){var r=31-Fo(t),o=1<<r;e[r]=-1,t&=~o}}function I0(e){if((_e&6)!==0)throw Error(ee(327));$a();var t=Hu(e,0);if((t&1)===0)return Dr(e,xt()),null;var r=pd(e,t);if(e.tag!==0&&r===2){var o=dh(e);o!==0&&(t=o,r=Bh(e,o))}if(r===1)throw r=zp,Ys(e,0),rs(e,t),Dr(e,xt()),r;if(r===6)throw Error(ee(345));return e.finishedWork=e.current.alternate,e.finishedLanes=t,Hs(e,Nr,Tn),Dr(e,xt()),null}function $g(e,t){var r=_e;_e|=1;try{return e(t)}finally{_e=r,_e===0&&(Oa=xt()+500,hd&&gs())}}function ti(e){ns!==null&&ns.tag===0&&(_e&6)===0&&$a();var t=_e;_e|=1;var r=co.transition,o=De;try{if(co.transition=null,De=1,e)return e()}finally{De=o,co.transition=r,_e=t,(_e&6)===0&&gs()}}function wg(){Kr=va.current,Ye(va)}function Ys(e,t){e.finishedWork=null,e.finishedLanes=0;var r=e.timeoutHandle;if(r!==-1&&(e.timeoutHandle=-1,D2(r)),Rt!==null)for(r=Rt.return;r!==null;){var o=r;switch(sg(o),o.tag){case 1:o=o.type.childContextTypes,o!=null&&Xu();break;case 3:Sa(),Ye(Ir),Ye(lr),mg();break;case 5:fg(o);break;case 4:Sa();break;case 13:Ye(it);break;case 19:Ye(it);break;case 10:pg(o.type._context);break;case 22:case 23:wg()}r=r.return}if(Bt=e,Rt=e=ds(e.current,null),Qt=Kr=t,Ot=0,zp=null,Pg=Td=ei=0,Nr=bp=null,Ks!==null){for(t=0;t<Ks.length;t++)if(r=Ks[t],o=r.interleaved,o!==null){r.interleaved=null;var n=o.next,s=r.pending;if(s!==null){var i=s.next;s.next=n,o.next=i}r.pending=o}Ks=null}return e}function w1(e,t){do{var r=Rt;try{if(lg(),ju.current=sd,nd){for(var o=at.memoizedState;o!==null;){var n=o.queue;n!==null&&(n.pending=null),o=o.next}nd=!1}if(Js=0,zt=kt=at=null,xp=!1,Dp=0,bg.current=null,r===null||r.return===null){Ot=1,zp=t,Rt=null;break}e:{var s=e,i=r.return,a=r,l=t;if(t=Qt,a.flags|=32768,l!==null&&typeof l=="object"&&typeof l.then=="function"){var p=l,c=a,u=c.tag;if((c.mode&1)===0&&(u===0||u===11||u===15)){var f=c.alternate;f?(c.updateQueue=f.updateQueue,c.memoizedState=f.memoizedState,c.lanes=f.lanes):(c.updateQueue=null,c.memoizedState=null)}var v=b0(i);if(v!==null){v.flags&=-257,P0(v,i,a,s,t),v.mode&1&&T0(s,p,t),t=v,l=p;var x=t.updateQueue;if(x===null){var h=new Set;h.add(l),t.updateQueue=h}else x.add(l);break e}else{if((t&1)===0){T0(s,p,t),_g();break e}l=Error(ee(426))}}else if(tt&&a.mode&1){var b=b0(i);if(b!==null){(b.flags&65536)===0&&(b.flags|=256),P0(b,i,a,s,t),ig(ka(l,a));break e}}s=l=ka(l,a),Ot!==4&&(Ot=2),bp===null?bp=[s]:bp.push(s),s=i;do{switch(s.tag){case 3:s.flags|=65536,t&=-t,s.lanes|=t;var y=l1(s,l,t);m0(s,y);break e;case 1:a=l;var m=s.type,g=s.stateNode;if((s.flags&128)===0&&(typeof m.getDerivedStateFromError=="function"||g!==null&&typeof g.componentDidCatch=="function"&&(cs===null||!cs.has(g)))){s.flags|=65536,t&=-t,s.lanes|=t;var T=p1(s,a,t);m0(s,T);break e}}s=s.return}while(s!==null)}E1(r)}catch(w){t=w,Rt===r&&r!==null&&(Rt=r=r.return);continue}break}while(!0)}function _1(){var e=id.current;return id.current=sd,e===null?sd:e}function _g(){(Ot===0||Ot===3||Ot===2)&&(Ot=4),Bt===null||(ei&268435455)===0&&(Td&268435455)===0||rs(Bt,Qt)}function pd(e,t){var r=_e;_e|=2;var o=_1();(Bt!==e||Qt!==t)&&(Tn=null,Ys(e,t));do try{aM();break}catch(n){w1(e,n)}while(!0);if(lg(),_e=r,id.current=o,Rt!==null)throw Error(ee(261));return Bt=null,Qt=0,Ot}function aM(){for(;Rt!==null;)R1(Rt)}function lM(){for(;Rt!==null&&!jN();)R1(Rt)}function R1(e){var t=k1(e.alternate,e,Kr);e.memoizedProps=e.pendingProps,t===null?E1(e):Rt=t,bg.current=null}function E1(e){var t=e;do{var r=t.alternate;if(e=t.return,(t.flags&32768)===0){if(r=eM(r,t,Kr),r!==null){Rt=r;return}}else{if(r=tM(r,t),r!==null){r.flags&=32767,Rt=r;return}if(e!==null)e.flags|=32768,e.subtreeFlags=0,e.deletions=null;else{Ot=6,Rt=null;return}}if(t=t.sibling,t!==null){Rt=t;return}Rt=t=e}while(t!==null);Ot===0&&(Ot=5)}function Hs(e,t,r){var o=De,n=co.transition;try{co.transition=null,De=1,pM(e,t,r,o)}finally{co.transition=n,De=o}return null}function pM(e,t,r,o){do $a();while(ns!==null);if((_e&6)!==0)throw Error(ee(327));r=e.finishedWork;var n=e.finishedLanes;if(r===null)return null;if(e.finishedWork=null,e.finishedLanes=0,r===e.current)throw Error(ee(177));e.callbackNode=null,e.callbackPriority=0;var s=r.lanes|r.childLanes;if(HN(e,s),e===Bt&&(Rt=Bt=null,Qt=0),(r.subtreeFlags&2064)===0&&(r.flags&2064)===0||ku||(ku=!0,O1(Vu,function(){return $a(),null})),s=(r.flags&15990)!==0,(r.subtreeFlags&15990)!==0||s){s=co.transition,co.transition=null;var i=De;De=1;var a=_e;_e|=4,bg.current=null,oM(e,r),P1(r,e),O2(vh),qu=!!gh,vh=gh=null,e.current=r,nM(r,e,n),DN(),_e=a,De=i,co.transition=s}else e.current=r;if(ku&&(ku=!1,ns=e,ld=n),s=e.pendingLanes,s===0&&(cs=null),zN(r.stateNode,o),Dr(e,xt()),t!==null)for(o=e.onRecoverableError,r=0;r<t.length;r++)n=t[r],o(n.value,{componentStack:n.stack,digest:n.digest});if(ad)throw ad=!1,e=Ah,Ah=null,e;return(ld&1)!==0&&e.tag!==0&&$a(),s=e.pendingLanes,(s&1)!==0?e===zh?Pp++:(Pp=0,zh=e):Pp=0,gs(),null}function $a(){if(ns!==null){var e=lP(ld),t=co.transition,r=De;try{if(co.transition=null,De=16>e?16:e,ns===null)var o=!1;else{if(e=ns,ns=null,ld=0,(_e&6)!==0)throw Error(ee(331));var n=_e;for(_e|=4,oe=e.current;oe!==null;){var s=oe,i=s.child;if((oe.flags&16)!==0){var a=s.deletions;if(a!==null){for(var l=0;l<a.length;l++){var p=a[l];for(oe=p;oe!==null;){var c=oe;switch(c.tag){case 0:case 11:case 15:Tp(8,c,s)}var u=c.child;if(u!==null)u.return=c,oe=u;else for(;oe!==null;){c=oe;var f=c.sibling,v=c.return;if(x1(c),c===p){oe=null;break}if(f!==null){f.return=v,oe=f;break}oe=v}}}var x=s.alternate;if(x!==null){var h=x.child;if(h!==null){x.child=null;do{var b=h.sibling;h.sibling=null,h=b}while(h!==null)}}oe=s}}if((s.subtreeFlags&2064)!==0&&i!==null)i.return=s,oe=i;else e:for(;oe!==null;){if(s=oe,(s.flags&2048)!==0)switch(s.tag){case 0:case 11:case 15:Tp(9,s,s.return)}var y=s.sibling;if(y!==null){y.return=s.return,oe=y;break e}oe=s.return}}var m=e.current;for(oe=m;oe!==null;){i=oe;var g=i.child;if((i.subtreeFlags&2064)!==0&&g!==null)g.return=i,oe=g;else e:for(i=m;oe!==null;){if(a=oe,(a.flags&2048)!==0)try{switch(a.tag){case 0:case 11:case 15:xd(9,a)}}catch(w){mt(a,a.return,w)}if(a===i){oe=null;break e}var T=a.sibling;if(T!==null){T.return=a.return,oe=T;break e}oe=a.return}}if(_e=n,gs(),ln&&typeof ln.onPostCommitFiberRoot=="function")try{ln.onPostCommitFiberRoot(ud,e)}catch{}o=!0}return o}finally{De=r,co.transition=t}}return!1}function j0(e,t,r){t=ka(r,t),t=l1(e,t,1),e=ps(e,t,1),t=xr(),e!==null&&(Bp(e,1,t),Dr(e,t))}function mt(e,t,r){if(e.tag===3)j0(e,e,r);else for(;t!==null;){if(t.tag===3){j0(t,e,r);break}else if(t.tag===1){var o=t.stateNode;if(typeof t.type.getDerivedStateFromError=="function"||typeof o.componentDidCatch=="function"&&(cs===null||!cs.has(o))){e=ka(r,e),e=p1(t,e,1),t=ps(t,e,1),e=xr(),t!==null&&(Bp(t,1,e),Dr(t,e));break}}t=t.return}}function cM(e,t,r){var o=e.pingCache;o!==null&&o.delete(t),t=xr(),e.pingedLanes|=e.suspendedLanes&r,Bt===e&&(Qt&r)===r&&(Ot===4||Ot===3&&(Qt&130023424)===Qt&&500>xt()-Cg?Ys(e,0):Pg|=r),Dr(e,t)}function S1(e,t){t===0&&((e.mode&1)===0?t=1:(t=hu,hu<<=1,(hu&130023424)===0&&(hu=4194304)));var r=xr();e=Rn(e,t),e!==null&&(Bp(e,t,r),Dr(e,r))}function uM(e){var t=e.memoizedState,r=0;t!==null&&(r=t.retryLane),S1(e,r)}function dM(e,t){var r=0;switch(e.tag){case 13:var o=e.stateNode,n=e.memoizedState;n!==null&&(r=n.retryLane);break;case 19:o=e.stateNode;break;default:throw Error(ee(314))}o!==null&&o.delete(t),S1(e,r)}var k1;k1=function(e,t,r){if(e!==null)if(e.memoizedProps!==t.pendingProps||Ir.current)Mr=!0;else{if((e.lanes&r)===0&&(t.flags&128)===0)return Mr=!1,J2(e,t,r);Mr=(e.flags&131072)!==0}else Mr=!1,tt&&(t.flags&1048576)!==0&&IP(t,Ju,t.index);switch(t.lanes=0,t.tag){case 2:var o=t.type;Lu(e,t),e=t.pendingProps;var n=_a(t,lr.current);Ca(t,r),n=hg(null,t,o,e,n,r);var s=gg();return t.flags|=1,typeof n=="object"&&n!==null&&typeof n.render=="function"&&n.$$typeof===void 0?(t.tag=1,t.memoizedState=null,t.updateQueue=null,jr(o)?(s=!0,Qu(t)):s=!1,t.memoizedState=n.state!==null&&n.state!==void 0?n.state:null,ug(t),n.updater=vd,t.stateNode=n,n._reactInternals=t,Rh(t,o,e,r),t=kh(null,t,o,!0,s,r)):(t.tag=0,tt&&s&&ng(t),vr(null,t,n,r),t=t.child),t;case 16:o=t.elementType;e:{switch(Lu(e,t),e=t.pendingProps,n=o._init,o=n(o._payload),t.type=o,n=t.tag=mM(o),e=Ao(o,e),n){case 0:t=Sh(null,t,o,e,r);break e;case 1:t=w0(null,t,o,e,r);break e;case 11:t=C0(null,t,o,e,r);break e;case 14:t=$0(null,t,o,Ao(o.type,e),r);break e}throw Error(ee(306,o,""))}return t;case 0:return o=t.type,n=t.pendingProps,n=t.elementType===o?n:Ao(o,n),Sh(e,t,o,n,r);case 1:return o=t.type,n=t.pendingProps,n=t.elementType===o?n:Ao(o,n),w0(e,t,o,n,r);case 3:e:{if(f1(t),e===null)throw Error(ee(387));o=t.pendingProps,s=t.memoizedState,n=s.element,BP(e,t),rd(t,o,null,r);var i=t.memoizedState;if(o=i.element,s.isDehydrated)if(s={element:o,isDehydrated:!1,cache:i.cache,pendingSuspenseBoundaries:i.pendingSuspenseBoundaries,transitions:i.transitions},t.updateQueue.baseState=s,t.memoizedState=s,t.flags&256){n=ka(Error(ee(423)),t),t=_0(e,t,o,r,n);break e}else if(o!==n){n=ka(Error(ee(424)),t),t=_0(e,t,o,r,n);break e}else for(Gr=ls(t.stateNode.containerInfo.firstChild),Yr=t,tt=!0,Bo=null,r=AP(t,null,o,r),t.child=r;r;)r.flags=r.flags&-3|4096,r=r.sibling;else{if(Ra(),o===n){t=En(e,t,r);break e}vr(e,t,o,r)}t=t.child}return t;case 5:return FP(t),e===null&&$h(t),o=t.type,n=t.pendingProps,s=e!==null?e.memoizedProps:null,i=n.children,xh(o,n)?i=null:s!==null&&xh(o,s)&&(t.flags|=32),d1(e,t),vr(e,t,i,r),t.child;case 6:return e===null&&$h(t),null;case 13:return m1(e,t,r);case 4:return dg(t,t.stateNode.containerInfo),o=t.pendingProps,e===null?t.child=Ea(t,null,o,r):vr(e,t,o,r),t.child;case 11:return o=t.type,n=t.pendingProps,n=t.elementType===o?n:Ao(o,n),C0(e,t,o,n,r);case 7:return vr(e,t,t.pendingProps,r),t.child;case 8:return vr(e,t,t.pendingProps.children,r),t.child;case 12:return vr(e,t,t.pendingProps.children,r),t.child;case 10:e:{if(o=t.type._context,n=t.pendingProps,s=t.memoizedProps,i=n.value,He(ed,o._currentValue),o._currentValue=i,s!==null)if(Wo(s.value,i)){if(s.children===n.children&&!Ir.current){t=En(e,t,r);break e}}else for(s=t.child,s!==null&&(s.return=t);s!==null;){var a=s.dependencies;if(a!==null){i=s.child;for(var l=a.firstContext;l!==null;){if(l.context===o){if(s.tag===1){l=$n(-1,r&-r),l.tag=2;var p=s.updateQueue;if(p!==null){p=p.shared;var c=p.pending;c===null?l.next=l:(l.next=c.next,c.next=l),p.pending=l}}s.lanes|=r,l=s.alternate,l!==null&&(l.lanes|=r),wh(s.return,r,t),a.lanes|=r;break}l=l.next}}else if(s.tag===10)i=s.type===t.type?null:s.child;else if(s.tag===18){if(i=s.return,i===null)throw Error(ee(341));i.lanes|=r,a=i.alternate,a!==null&&(a.lanes|=r),wh(i,r,t),i=s.sibling}else i=s.child;if(i!==null)i.return=s;else for(i=s;i!==null;){if(i===t){i=null;break}if(s=i.sibling,s!==null){s.return=i.return,i=s;break}i=i.return}s=i}vr(e,t,n.children,r),t=t.child}return t;case 9:return n=t.type,o=t.pendingProps.children,Ca(t,r),n=uo(n),o=o(n),t.flags|=1,vr(e,t,o,r),t.child;case 14:return o=t.type,n=Ao(o,t.pendingProps),n=Ao(o.type,n),$0(e,t,o,n,r);case 15:return c1(e,t,t.type,t.pendingProps,r);case 17:return o=t.type,n=t.pendingProps,n=t.elementType===o?n:Ao(o,n),Lu(e,t),t.tag=1,jr(o)?(e=!0,Qu(t)):e=!1,Ca(t,r),a1(t,o,n),Rh(t,o,n,r),kh(null,t,o,!0,e,r);case 19:return y1(e,t,r);case 22:return u1(e,t,r)}throw Error(ee(156,t.tag))};function O1(e,t){return nP(e,t)}function fM(e,t,r,o){this.tag=e,this.key=r,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=o,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function po(e,t,r,o){return new fM(e,t,r,o)}function Rg(e){return e=e.prototype,!(!e||!e.isReactComponent)}function mM(e){if(typeof e=="function")return Rg(e)?1:0;if(e!=null){if(e=e.$$typeof,e===qh)return 11;if(e===Kh)return 14}return 2}function ds(e,t){var r=e.alternate;return r===null?(r=po(e.tag,t,e.key,e.mode),r.elementType=e.elementType,r.type=e.type,r.stateNode=e.stateNode,r.alternate=e,e.alternate=r):(r.pendingProps=t,r.type=e.type,r.flags=0,r.subtreeFlags=0,r.deletions=null),r.flags=e.flags&14680064,r.childLanes=e.childLanes,r.lanes=e.lanes,r.child=e.child,r.memoizedProps=e.memoizedProps,r.memoizedState=e.memoizedState,r.updateQueue=e.updateQueue,t=e.dependencies,r.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},r.sibling=e.sibling,r.index=e.index,r.ref=e.ref,r}function Bu(e,t,r,o,n,s){var i=2;if(o=e,typeof e=="function")Rg(e)&&(i=1);else if(typeof e=="string")i=5;else e:switch(e){case la:return Xs(r.children,n,s,t);case Hh:i=8,n|=8;break;case Qy:return e=po(12,r,t,n|2),e.elementType=Qy,e.lanes=s,e;case Zy:return e=po(13,r,t,n),e.elementType=Zy,e.lanes=s,e;case Jy:return e=po(19,r,t,n),e.elementType=Jy,e.lanes=s,e;case F0:return bd(r,n,s,t);default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case z0:i=10;break e;case B0:i=9;break e;case qh:i=11;break e;case Kh:i=14;break e;case Jn:i=16,o=null;break e}throw Error(ee(130,e==null?e:typeof e,""))}return t=po(i,r,t,n),t.elementType=e,t.type=o,t.lanes=s,t}function Xs(e,t,r,o){return e=po(7,e,o,t),e.lanes=r,e}function bd(e,t,r,o){return e=po(22,e,o,t),e.elementType=F0,e.lanes=r,e.stateNode={isHidden:!1},e}function Gy(e,t,r){return e=po(6,e,null,t),e.lanes=r,e}function Yy(e,t,r){return t=po(4,e.children!==null?e.children:[],e.key,t),t.lanes=r,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}function yM(e,t,r,o,n){this.tag=t,this.containerInfo=e,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=Ny(0),this.expirationTimes=Ny(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Ny(0),this.identifierPrefix=o,this.onRecoverableError=n,this.mutableSourceEagerHydrationData=null}function Eg(e,t,r,o,n,s,i,a,l){return e=new yM(e,t,r,a,l),t===1?(t=1,s===!0&&(t|=8)):t=0,s=po(3,null,null,t),e.current=s,s.stateNode=e,s.memoizedState={element:o,isDehydrated:r,cache:null,transitions:null,pendingSuspenseBoundaries:null},ug(s),e}function hM(e,t,r){var o=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:aa,key:o==null?null:""+o,children:e,containerInfo:t,implementation:r}}function N1(e){if(!e)return ms;e=e._reactInternals;e:{if(oi(e)!==e||e.tag!==1)throw Error(ee(170));var t=e;do{switch(t.tag){case 3:t=t.stateNode.context;break e;case 1:if(jr(t.type)){t=t.stateNode.__reactInternalMemoizedMergedChildContext;break e}}t=t.return}while(t!==null);throw Error(ee(171))}if(e.tag===1){var r=e.type;if(jr(r))return NP(e,r,t)}return t}function M1(e,t,r,o,n,s,i,a,l){return e=Eg(r,o,!0,e,n,s,i,a,l),e.context=N1(null),r=e.current,o=xr(),n=us(r),s=$n(o,n),s.callback=t??null,ps(r,s,n),e.current.lanes=n,Bp(e,n,o),Dr(e,o),e}function Pd(e,t,r,o){var n=t.current,s=xr(),i=us(n);return r=N1(r),t.context===null?t.context=r:t.pendingContext=r,t=$n(s,i),t.payload={element:e},o=o===void 0?null:o,o!==null&&(t.callback=o),e=ps(n,t,i),e!==null&&(Uo(e,n,i,s),Iu(e,n,i)),i}function cd(e){if(e=e.current,!e.child)return null;switch(e.child.tag){case 5:return e.child.stateNode;default:return e.child.stateNode}}function D0(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var r=e.retryLane;e.retryLane=r!==0&&r<t?r:t}}function Sg(e,t){D0(e,t),(e=e.alternate)&&D0(e,t)}function gM(){return null}var I1=typeof reportError=="function"?reportError:function(e){console.error(e)};function kg(e){this._internalRoot=e}Cd.prototype.render=kg.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(ee(409));Pd(e,t,null,null)};Cd.prototype.unmount=kg.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;ti(function(){Pd(null,e,null,null)}),t[_n]=null}};function Cd(e){this._internalRoot=e}Cd.prototype.unstable_scheduleHydration=function(e){if(e){var t=uP();e={blockedOn:null,target:e,priority:t};for(var r=0;r<ts.length&&t!==0&&t<ts[r].priority;r++);ts.splice(r,0,e),r===0&&fP(e)}};function Og(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function $d(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11&&(e.nodeType!==8||e.nodeValue!==" react-mount-point-unstable "))}function L0(){}function vM(e,t,r,o,n){if(n){if(typeof o=="function"){var s=o;o=function(){var p=cd(i);s.call(p)}}var i=M1(t,o,e,0,null,!1,!1,"",L0);return e._reactRootContainer=i,e[_n]=i.current,Op(e.nodeType===8?e.parentNode:e),ti(),i}for(;n=e.lastChild;)e.removeChild(n);if(typeof o=="function"){var a=o;o=function(){var p=cd(l);a.call(p)}}var l=Eg(e,0,!1,null,null,!1,!1,"",L0);return e._reactRootContainer=l,e[_n]=l.current,Op(e.nodeType===8?e.parentNode:e),ti(function(){Pd(t,l,r,o)}),l}function wd(e,t,r,o,n){var s=r._reactRootContainer;if(s){var i=s;if(typeof n=="function"){var a=n;n=function(){var l=cd(i);a.call(l)}}Pd(t,i,e,n)}else i=vM(r,t,e,n,o);return cd(i)}pP=function(e){switch(e.tag){case 3:var t=e.stateNode;if(t.current.memoizedState.isDehydrated){var r=dp(t.pendingLanes);r!==0&&(Xh(t,r|1),Dr(t,xt()),(_e&6)===0&&(Oa=xt()+500,gs()))}break;case 13:ti(function(){var o=Rn(e,1);if(o!==null){var n=xr();Uo(o,e,1,n)}}),Sg(e,1)}};Qh=function(e){if(e.tag===13){var t=Rn(e,134217728);if(t!==null){var r=xr();Uo(t,e,134217728,r)}Sg(e,134217728)}};cP=function(e){if(e.tag===13){var t=us(e),r=Rn(e,t);if(r!==null){var o=xr();Uo(r,e,t,o)}Sg(e,t)}};uP=function(){return De};dP=function(e,t){var r=De;try{return De=e,t()}finally{De=r}};ph=function(e,t,r){switch(t){case"input":if(rh(e,r),t=r.name,r.type==="radio"&&t!=null){for(r=e;r.parentNode;)r=r.parentNode;for(r=r.querySelectorAll("input[name="+JSON.stringify(""+t)+'][type="radio"]'),t=0;t<r.length;t++){var o=r[t];if(o!==e&&o.form===e.form){var n=yd(o);if(!n)throw Error(ee(90));W0(o),rh(o,n)}}}break;case"textarea":H0(e,r);break;case"select":t=r.value,t!=null&&xa(e,!!r.multiple,t,!1)}};Z0=$g;J0=ti;var xM={usingClientEntryPoint:!1,Events:[Up,da,yd,X0,Q0,$g]},lp={findFiberByHostInstance:qs,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},TM={bundleType:lp.bundleType,version:lp.version,rendererPackageName:lp.rendererPackageName,rendererConfig:lp.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:Sn.ReactCurrentDispatcher,findHostInstanceByFiber:function(e){return e=rP(e),e===null?null:e.stateNode},findFiberByHostInstance:lp.findFiberByHostInstance||gM,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"&&(pp=__REACT_DEVTOOLS_GLOBAL_HOOK__,!pp.isDisabled&&pp.supportsFiber))try{ud=pp.inject(TM),ln=pp}catch{}var pp;Zr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=xM;Zr.createPortal=function(e,t){var r=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!Og(t))throw Error(ee(200));return hM(e,t,null,r)};Zr.createRoot=function(e,t){if(!Og(e))throw Error(ee(299));var r=!1,o="",n=I1;return t!=null&&(t.unstable_strictMode===!0&&(r=!0),t.identifierPrefix!==void 0&&(o=t.identifierPrefix),t.onRecoverableError!==void 0&&(n=t.onRecoverableError)),t=Eg(e,1,!1,null,null,r,!1,o,n),e[_n]=t.current,Op(e.nodeType===8?e.parentNode:e),new kg(t)};Zr.findDOMNode=function(e){if(e==null)return null;if(e.nodeType===1)return e;var t=e._reactInternals;if(t===void 0)throw typeof e.render=="function"?Error(ee(188)):(e=Object.keys(e).join(","),Error(ee(268,e)));return e=rP(t),e=e===null?null:e.stateNode,e};Zr.flushSync=function(e){return ti(e)};Zr.hydrate=function(e,t,r){if(!$d(t))throw Error(ee(200));return wd(null,e,t,!0,r)};Zr.hydrateRoot=function(e,t,r){if(!Og(e))throw Error(ee(405));var o=r!=null&&r.hydratedSources||null,n=!1,s="",i=I1;if(r!=null&&(r.unstable_strictMode===!0&&(n=!0),r.identifierPrefix!==void 0&&(s=r.identifierPrefix),r.onRecoverableError!==void 0&&(i=r.onRecoverableError)),t=M1(t,null,e,1,r??null,n,!1,s,i),e[_n]=t.current,Op(e),o)for(e=0;e<o.length;e++)r=o[e],n=r._getVersion,n=n(r._source),t.mutableSourceEagerHydrationData==null?t.mutableSourceEagerHydrationData=[r,n]:t.mutableSourceEagerHydrationData.push(r,n);return new Cd(t)};Zr.render=function(e,t,r){if(!$d(t))throw Error(ee(200));return wd(null,e,t,!1,r)};Zr.unmountComponentAtNode=function(e){if(!$d(e))throw Error(ee(40));return e._reactRootContainer?(ti(function(){wd(null,null,e,!1,function(){e._reactRootContainer=null,e[_n]=null})}),!0):!1};Zr.unstable_batchedUpdates=$g;Zr.unstable_renderSubtreeIntoContainer=function(e,t,r,o){if(!$d(r))throw Error(ee(200));if(e==null||e._reactInternals===void 0)throw Error(ee(38));return wd(e,t,r,!1,o)};Zr.version="18.3.1-next-f1338f8080-20240426"});var _d=se((UW,L1)=>{"use strict";function D1(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(D1)}catch(e){console.error(e)}}D1(),L1.exports=j1()});var z1=se(Ng=>{"use strict";var A1=_d();Ng.createRoot=A1.createRoot,Ng.hydrateRoot=A1.hydrateRoot;var WW});function d(){return d=Object.assign?Object.assign.bind():function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var o in r)({}).hasOwnProperty.call(r,o)&&(e[o]=r[o])}return e},d.apply(null,arguments)}var J=et(()=>{});var V1=se((GW,W1)=>{"use strict";var bM="SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED";W1.exports=bM});var G1=se((YW,K1)=>{"use strict";var PM=V1();function H1(){}function q1(){}q1.resetWarningCache=H1;K1.exports=function(){function e(o,n,s,i,a,l){if(l!==PM){var p=new Error("Calling PropTypes validators directly is not supported by the `prop-types` package. Use PropTypes.checkPropTypes() to call them. Read more at http://fb.me/use-check-prop-types");throw p.name="Invariant Violation",p}}e.isRequired=e;function t(){return e}var r={array:e,bigint:e,bool:e,func:e,number:e,object:e,string:e,symbol:e,any:e,arrayOf:t,element:e,elementType:e,instanceOf:t,node:e,objectOf:t,oneOf:t,oneOfType:t,shape:t,exact:t,checkPropTypes:q1,resetWarningCache:H1};return r.PropTypes=r,r}});var Vp=se((ZW,Y1)=>{Y1.exports=G1()();var XW,QW});var Le=se((JW,Hp)=>{function CM(e){return e&&e.__esModule?e:{default:e}}Hp.exports=CM,Hp.exports.__esModule=!0,Hp.exports.default=Hp.exports});var X1=se(Mg=>{"use strict";Object.defineProperty(Mg,"__esModule",{value:!0});Mg.default=$M;function $M(e){let t="https://mui.com/production-error/?code="+e;for(let r=1;r<arguments.length;r+=1)t+="&args[]="+encodeURIComponent(arguments[r]);return"Minified MUI error #"+e+"; visit "+t+" for the full message."}});var ni=se(Ig=>{"use strict";var wM=Le();Object.defineProperty(Ig,"__esModule",{value:!0});Object.defineProperty(Ig,"default",{enumerable:!0,get:function(){return _M.default}});var _M=wM(X1())});function EM(e){if(e.sheet)return e.sheet;for(var t=0;t<document.styleSheets.length;t++)if(document.styleSheets[t].ownerNode===e)return document.styleSheets[t]}function SM(e){var t=document.createElement("style");return t.setAttribute("data-emotion",e.key),e.nonce!==void 0&&t.setAttribute("nonce",e.nonce),t.appendChild(document.createTextNode("")),t.setAttribute("data-s",""),t}var RM,Q1,Z1=et(()=>{RM=!1;Q1=(function(){function e(r){var o=this;this._insertTag=function(n){var s;o.tags.length===0?o.insertionPoint?s=o.insertionPoint.nextSibling:o.prepend?s=o.container.firstChild:s=o.before:s=o.tags[o.tags.length-1].nextSibling,o.container.insertBefore(n,s),o.tags.push(n)},this.isSpeedy=r.speedy===void 0?!RM:r.speedy,this.tags=[],this.ctr=0,this.nonce=r.nonce,this.key=r.key,this.container=r.container,this.prepend=r.prepend,this.insertionPoint=r.insertionPoint,this.before=null}var t=e.prototype;return t.hydrate=function(o){o.forEach(this._insertTag)},t.insert=function(o){this.ctr%(this.isSpeedy?65e3:1)===0&&this._insertTag(SM(this));var n=this.tags[this.tags.length-1];if(this.isSpeedy){var s=EM(n);try{s.insertRule(o,s.cssRules.length)}catch{}}else n.appendChild(document.createTextNode(o));this.ctr++},t.flush=function(){this.tags.forEach(function(o){var n;return(n=o.parentNode)==null?void 0:n.removeChild(o)}),this.tags=[],this.ctr=0},e})()});var Jt,qp,ke,Rd,Ia,ja,J1,Ed,eC,Sd=et(()=>{Jt="-ms-",qp="-moz-",ke="-webkit-",Rd="comm",Ia="rule",ja="decl",J1="@import",Ed="@keyframes",eC="@layer"});function oC(e,t){return Tt(e,0)^45?(((t<<2^Tt(e,0))<<2^Tt(e,1))<<2^Tt(e,2))<<2^Tt(e,3):0}function kd(e){return e.trim()}function jg(e,t){return(e=t.exec(e))?e[0]:e}function we(e,t,r){return e.replace(t,r)}function Kp(e,t){return e.indexOf(t)}function Tt(e,t){return e.charCodeAt(t)|0}function vs(e,t,r){return e.slice(t,r)}function br(e){return e.length}function Da(e){return e.length}function La(e,t){return t.push(e),e}function Dg(e,t){return e.map(t).join("")}var tC,si,rC,Aa=et(()=>{tC=Math.abs,si=String.fromCharCode,rC=Object.assign});function Gp(e,t,r,o,n,s,i){return{value:e,root:t,parent:r,type:o,props:n,children:s,line:Od,column:za,length:i,return:""}}function Ua(e,t){return rC(Gp("",null,null,"",null,null,0),e,{length:-e.length},t)}function sC(){return Et}function iC(){return Et=Pr>0?Tt(Fa,--Pr):0,za--,Et===10&&(za=1,Od--),Et}function Cr(){return Et=Pr<nC?Tt(Fa,Pr++):0,za++,Et===10&&(za=1,Od++),Et}function mo(){return Tt(Fa,Pr)}function Yp(){return Pr}function Wa(e,t){return vs(Fa,e,t)}function Ba(e){switch(e){case 0:case 9:case 10:case 13:case 32:return 5;case 33:case 43:case 44:case 47:case 62:case 64:case 126:case 59:case 123:case 125:return 4;case 58:return 3;case 34:case 39:case 40:case 91:return 2;case 41:case 93:return 1}return 0}function Nd(e){return Od=za=1,nC=br(Fa=e),Pr=0,[]}function Md(e){return Fa="",e}function Va(e){return kd(Wa(Pr-1,Lg(e===91?e+2:e===40?e+1:e)))}function aC(e){for(;(Et=mo())&&Et<33;)Cr();return Ba(e)>2||Ba(Et)>3?"":" "}function lC(e,t){for(;--t&&Cr()&&!(Et<48||Et>102||Et>57&&Et<65||Et>70&&Et<97););return Wa(e,Yp()+(t<6&&mo()==32&&Cr()==32))}function Lg(e){for(;Cr();)switch(Et){case e:return Pr;case 34:case 39:e!==34&&e!==39&&Lg(Et);break;case 40:e===41&&Lg(e);break;case 92:Cr();break}return Pr}function pC(e,t){for(;Cr()&&e+Et!==57;)if(e+Et===84&&mo()===47)break;return"/*"+Wa(t,Pr-1)+"*"+si(e===47?e:Cr())}function cC(e){for(;!Ba(mo());)Cr();return Wa(e,Pr)}var Od,za,nC,Pr,Et,Fa,Ag=et(()=>{Aa();Od=1,za=1,nC=0,Pr=0,Et=0,Fa=""});function fC(e){return Md(Id("",null,null,null,[""],e=Nd(e),0,[0],e))}function Id(e,t,r,o,n,s,i,a,l){for(var p=0,c=0,u=i,f=0,v=0,x=0,h=1,b=1,y=1,m=0,g="",T=n,w=s,$=o,C=g;b;)switch(x=m,m=Cr()){case 40:if(x!=108&&Tt(C,u-1)==58){Kp(C+=we(Va(m),"&","&\f"),"&\f")!=-1&&(y=-1);break}case 34:case 39:case 91:C+=Va(m);break;case 9:case 10:case 13:case 32:C+=aC(x);break;case 92:C+=lC(Yp()-1,7);continue;case 47:switch(mo()){case 42:case 47:La(kM(pC(Cr(),Yp()),t,r),l);break;default:C+="/"}break;case 123*h:a[p++]=br(C)*y;case 125*h:case 59:case 0:switch(m){case 0:case 125:b=0;case 59+c:y==-1&&(C=we(C,/\f/g,"")),v>0&&br(C)-u&&La(v>32?dC(C+";",o,r,u-1):dC(we(C," ","")+";",o,r,u-2),l);break;case 59:C+=";";default:if(La($=uC(C,t,r,p,c,n,a,g,T=[],w=[],u),s),m===123)if(c===0)Id(C,t,$,$,T,s,u,a,w);else switch(f===99&&Tt(C,3)===110?100:f){case 100:case 108:case 109:case 115:Id(e,$,$,o&&La(uC(e,$,$,0,0,n,a,g,n,T=[],u),w),n,w,u,a,o?T:w);break;default:Id(C,$,$,$,[""],w,0,a,w)}}p=c=v=0,h=y=1,g=C="",u=i;break;case 58:u=1+br(C),v=x;default:if(h<1){if(m==123)--h;else if(m==125&&h++==0&&iC()==125)continue}switch(C+=si(m),m*h){case 38:y=c>0?1:(C+="\f",-1);break;case 44:a[p++]=(br(C)-1)*y,y=1;break;case 64:mo()===45&&(C+=Va(Cr())),f=mo(),c=u=br(g=C+=cC(Yp())),m++;break;case 45:x===45&&br(C)==2&&(h=0)}}return s}function uC(e,t,r,o,n,s,i,a,l,p,c){for(var u=n-1,f=n===0?s:[""],v=Da(f),x=0,h=0,b=0;x<o;++x)for(var y=0,m=vs(e,u+1,u=tC(h=i[x])),g=e;y<v;++y)(g=kd(h>0?f[y]+" "+m:we(m,/&\f/g,f[y])))&&(l[b++]=g);return Gp(e,t,r,n===0?Ia:a,l,p,c)}function kM(e,t,r){return Gp(e,t,r,Rd,si(sC()),vs(e,2,-2),0)}function dC(e,t,r,o){return Gp(e,t,r,ja,vs(e,0,o),vs(e,o+1,-1),o)}var mC=et(()=>{Sd();Aa();Ag()});var yC=et(()=>{});function ii(e,t){for(var r="",o=Da(e),n=0;n<o;n++)r+=t(e[n],n,e,t)||"";return r}function hC(e,t,r,o){switch(e.type){case eC:if(e.children.length)break;case J1:case ja:return e.return=e.return||e.value;case Rd:return"";case Ed:return e.return=e.value+"{"+ii(e.children,o)+"}";case Ia:e.value=e.props.join(",")}return br(r=ii(e.children,o))?e.return=e.value+"{"+r+"}":""}var gC=et(()=>{Sd();Aa()});function vC(e){var t=Da(e);return function(r,o,n,s){for(var i="",a=0;a<t;a++)i+=e[a](r,o,n,s)||"";return i}}function xC(e){return function(t){t.root||(t=t.return)&&e(t)}}var TC=et(()=>{Aa()});var bC=et(()=>{Sd();Aa();mC();yC();Ag();gC();TC()});var zg,jd=et(()=>{zg=function(t){var r=new WeakMap;return function(o){if(r.has(o))return r.get(o);var n=t(o);return r.set(o,n),n}}});function Dd(e){var t=Object.create(null);return function(r){return t[r]===void 0&&(t[r]=e(r)),t[r]}}var Ld=et(()=>{});var $C={};ou($C,{default:()=>Bg});function CC(e,t){switch(oC(e,t)){case 5103:return ke+"print-"+e+e;case 5737:case 4201:case 3177:case 3433:case 1641:case 4457:case 2921:case 5572:case 6356:case 5844:case 3191:case 6645:case 3005:case 6391:case 5879:case 5623:case 6135:case 4599:case 4855:case 4215:case 6389:case 5109:case 5365:case 5621:case 3829:return ke+e+e;case 5349:case 4246:case 4810:case 6968:case 2756:return ke+e+qp+e+Jt+e+e;case 6828:case 4268:return ke+e+Jt+e+e;case 6165:return ke+e+Jt+"flex-"+e+e;case 5187:return ke+e+we(e,/(\w+).+(:[^]+)/,ke+"box-$1$2"+Jt+"flex-$1$2")+e;case 5443:return ke+e+Jt+"flex-item-"+we(e,/flex-|-self/,"")+e;case 4675:return ke+e+Jt+"flex-line-pack"+we(e,/align-content|flex-|-self/,"")+e;case 5548:return ke+e+Jt+we(e,"shrink","negative")+e;case 5292:return ke+e+Jt+we(e,"basis","preferred-size")+e;case 6060:return ke+"box-"+we(e,"-grow","")+ke+e+Jt+we(e,"grow","positive")+e;case 4554:return ke+we(e,/([^-])(transform)/g,"$1"+ke+"$2")+e;case 6187:return we(we(we(e,/(zoom-|grab)/,ke+"$1"),/(image-set)/,ke+"$1"),e,"")+e;case 5495:case 3959:return we(e,/(image-set\([^]*)/,ke+"$1$`$1");case 4968:return we(we(e,/(.+:)(flex-)?(.*)/,ke+"box-pack:$3"+Jt+"flex-pack:$3"),/s.+-b[^;]+/,"justify")+ke+e+e;case 4095:case 3583:case 4068:case 2532:return we(e,/(.+)-inline(.+)/,ke+"$1$2")+e;case 8116:case 7059:case 5753:case 5535:case 5445:case 5701:case 4933:case 4677:case 5533:case 5789:case 5021:case 4765:if(br(e)-1-t>6)switch(Tt(e,t+1)){case 109:if(Tt(e,t+4)!==45)break;case 102:return we(e,/(.+:)(.+)-([^]+)/,"$1"+ke+"$2-$3$1"+qp+(Tt(e,t+3)==108?"$3":"$2-$3"))+e;case 115:return~Kp(e,"stretch")?CC(we(e,"stretch","fill-available"),t)+e:e}break;case 4949:if(Tt(e,t+1)!==115)break;case 6444:switch(Tt(e,br(e)-3-(~Kp(e,"!important")&&10))){case 107:return we(e,":",":"+ke)+e;case 101:return we(e,/(.+:)([^;!]+)(;|!.+)?/,"$1"+ke+(Tt(e,14)===45?"inline-":"")+"box$3$1"+ke+"$2$3$1"+Jt+"$2box$3")+e}break;case 5936:switch(Tt(e,t+11)){case 114:return ke+e+Jt+we(e,/[svh]\w+-[tblr]{2}/,"tb")+e;case 108:return ke+e+Jt+we(e,/[svh]\w+-[tblr]{2}/,"tb-rl")+e;case 45:return ke+e+Jt+we(e,/[svh]\w+-[tblr]{2}/,"lr")+e}return ke+e+Jt+e+e}return e}var OM,NM,MM,PC,IM,jM,DM,LM,Bg,Ad=et(()=>{Z1();bC();jd();Ld();OM=function(t,r,o){for(var n=0,s=0;n=s,s=mo(),n===38&&s===12&&(r[o]=1),!Ba(s);)Cr();return Wa(t,Pr)},NM=function(t,r){var o=-1,n=44;do switch(Ba(n)){case 0:n===38&&mo()===12&&(r[o]=1),t[o]+=OM(Pr-1,r,o);break;case 2:t[o]+=Va(n);break;case 4:if(n===44){t[++o]=mo()===58?"&\f":"",r[o]=t[o].length;break}default:t[o]+=si(n)}while(n=Cr());return t},MM=function(t,r){return Md(NM(Nd(t),r))},PC=new WeakMap,IM=function(t){if(!(t.type!=="rule"||!t.parent||t.length<1)){for(var r=t.value,o=t.parent,n=t.column===o.column&&t.line===o.line;o.type!=="rule";)if(o=o.parent,!o)return;if(!(t.props.length===1&&r.charCodeAt(0)!==58&&!PC.get(o))&&!n){PC.set(t,!0);for(var s=[],i=MM(r,s),a=o.props,l=0,p=0;l<i.length;l++)for(var c=0;c<a.length;c++,p++)t.props[p]=s[l]?i[l].replace(/&\f/g,a[c]):a[c]+" "+i[l]}}},jM=function(t){if(t.type==="decl"){var r=t.value;r.charCodeAt(0)===108&&r.charCodeAt(2)===98&&(t.return="",t.value="")}};DM=function(t,r,o,n){if(t.length>-1&&!t.return)switch(t.type){case ja:t.return=CC(t.value,t.length);break;case Ed:return ii([Ua(t,{value:we(t.value,"@","@"+ke)})],n);case Ia:if(t.length)return Dg(t.props,function(s){switch(jg(s,/(::plac\w+|:read-\w+)/)){case":read-only":case":read-write":return ii([Ua(t,{props:[we(s,/:(read-\w+)/,":"+qp+"$1")]})],n);case"::placeholder":return ii([Ua(t,{props:[we(s,/:(plac\w+)/,":"+ke+"input-$1")]}),Ua(t,{props:[we(s,/:(plac\w+)/,":"+qp+"$1")]}),Ua(t,{props:[we(s,/:(plac\w+)/,Jt+"input-$1")]})],n)}return""})}},LM=[DM],Bg=function(t){var r=t.key;if(r==="css"){var o=document.querySelectorAll("style[data-emotion]:not([data-s])");Array.prototype.forEach.call(o,function(h){var b=h.getAttribute("data-emotion");b.indexOf(" ")!==-1&&(document.head.appendChild(h),h.setAttribute("data-s",""))})}var n=t.stylisPlugins||LM,s={},i,a=[];i=t.container||document.head,Array.prototype.forEach.call(document.querySelectorAll('style[data-emotion^="'+r+' "]'),function(h){for(var b=h.getAttribute("data-emotion").split(" "),y=1;y<b.length;y++)s[b[y]]=!0;a.push(h)});var l,p=[IM,jM];{var c,u=[hC,xC(function(h){c.insert(h)})],f=vC(p.concat(n,u)),v=function(b){return ii(fC(b),f)};l=function(b,y,m,g){c=m,v(b?b+"{"+y.styles+"}":y.styles),g&&(x.inserted[y.name]=!0)}}var x={key:r,sheet:new Q1({key:r,container:i,nonce:t.nonce,speedy:t.speedy,prepend:t.prepend,insertionPoint:t.insertionPoint}),nonce:t.nonce,inserted:s,registered:{},insert:l};return x.sheet.hydrate(a),x}});var _C=se(Ae=>{"use strict";var Ft=typeof Symbol=="function"&&Symbol.for,Fg=Ft?Symbol.for("react.element"):60103,Ug=Ft?Symbol.for("react.portal"):60106,zd=Ft?Symbol.for("react.fragment"):60107,Bd=Ft?Symbol.for("react.strict_mode"):60108,Fd=Ft?Symbol.for("react.profiler"):60114,Ud=Ft?Symbol.for("react.provider"):60109,Wd=Ft?Symbol.for("react.context"):60110,Wg=Ft?Symbol.for("react.async_mode"):60111,Vd=Ft?Symbol.for("react.concurrent_mode"):60111,Hd=Ft?Symbol.for("react.forward_ref"):60112,qd=Ft?Symbol.for("react.suspense"):60113,AM=Ft?Symbol.for("react.suspense_list"):60120,Kd=Ft?Symbol.for("react.memo"):60115,Gd=Ft?Symbol.for("react.lazy"):60116,zM=Ft?Symbol.for("react.block"):60121,BM=Ft?Symbol.for("react.fundamental"):60117,FM=Ft?Symbol.for("react.responder"):60118,UM=Ft?Symbol.for("react.scope"):60119;function Jr(e){if(typeof e=="object"&&e!==null){var t=e.$$typeof;switch(t){case Fg:switch(e=e.type,e){case Wg:case Vd:case zd:case Fd:case Bd:case qd:return e;default:switch(e=e&&e.$$typeof,e){case Wd:case Hd:case Gd:case Kd:case Ud:return e;default:return t}}case Ug:return t}}}function wC(e){return Jr(e)===Vd}Ae.AsyncMode=Wg;Ae.ConcurrentMode=Vd;Ae.ContextConsumer=Wd;Ae.ContextProvider=Ud;Ae.Element=Fg;Ae.ForwardRef=Hd;Ae.Fragment=zd;Ae.Lazy=Gd;Ae.Memo=Kd;Ae.Portal=Ug;Ae.Profiler=Fd;Ae.StrictMode=Bd;Ae.Suspense=qd;Ae.isAsyncMode=function(e){return wC(e)||Jr(e)===Wg};Ae.isConcurrentMode=wC;Ae.isContextConsumer=function(e){return Jr(e)===Wd};Ae.isContextProvider=function(e){return Jr(e)===Ud};Ae.isElement=function(e){return typeof e=="object"&&e!==null&&e.$$typeof===Fg};Ae.isForwardRef=function(e){return Jr(e)===Hd};Ae.isFragment=function(e){return Jr(e)===zd};Ae.isLazy=function(e){return Jr(e)===Gd};Ae.isMemo=function(e){return Jr(e)===Kd};Ae.isPortal=function(e){return Jr(e)===Ug};Ae.isProfiler=function(e){return Jr(e)===Fd};Ae.isStrictMode=function(e){return Jr(e)===Bd};Ae.isSuspense=function(e){return Jr(e)===qd};Ae.isValidElementType=function(e){return typeof e=="string"||typeof e=="function"||e===zd||e===Vd||e===Fd||e===Bd||e===qd||e===AM||typeof e=="object"&&e!==null&&(e.$$typeof===Gd||e.$$typeof===Kd||e.$$typeof===Ud||e.$$typeof===Wd||e.$$typeof===Hd||e.$$typeof===BM||e.$$typeof===FM||e.$$typeof===UM||e.$$typeof===zM)};Ae.typeOf=Jr});var EC=se((N8,RC)=>{"use strict";RC.exports=_C()});var qg=se((M8,IC)=>{"use strict";var Vg=EC(),WM={childContextTypes:!0,contextType:!0,contextTypes:!0,defaultProps:!0,displayName:!0,getDefaultProps:!0,getDerivedStateFromError:!0,getDerivedStateFromProps:!0,mixins:!0,propTypes:!0,type:!0},VM={name:!0,length:!0,prototype:!0,caller:!0,callee:!0,arguments:!0,arity:!0},HM={$$typeof:!0,render:!0,defaultProps:!0,displayName:!0,propTypes:!0},NC={$$typeof:!0,compare:!0,defaultProps:!0,displayName:!0,propTypes:!0,type:!0},Hg={};Hg[Vg.ForwardRef]=HM;Hg[Vg.Memo]=NC;function SC(e){return Vg.isMemo(e)?NC:Hg[e.$$typeof]||WM}var qM=Object.defineProperty,KM=Object.getOwnPropertyNames,kC=Object.getOwnPropertySymbols,GM=Object.getOwnPropertyDescriptor,YM=Object.getPrototypeOf,OC=Object.prototype;function MC(e,t,r){if(typeof t!="string"){if(OC){var o=YM(t);o&&o!==OC&&MC(e,o,r)}var n=KM(t);kC&&(n=n.concat(kC(t)));for(var s=SC(e),i=SC(t),a=0;a<n.length;++a){var l=n[a];if(!VM[l]&&!(r&&r[l])&&!(i&&i[l])&&!(s&&s[l])){var p=GM(t,l);try{qM(e,l,p)}catch{}}}}return e}IC.exports=MC});var jC,DC,LC=et(()=>{jC=P(qg()),DC=(function(e,t){return(0,jC.default)(e,t)})});function Ha(e,t,r){var o="";return r.split(" ").forEach(function(n){e[n]!==void 0?t.push(e[n]+";"):n&&(o+=n+" ")}),o}var XM,ai,li,Xp=et(()=>{XM=!0;ai=function(t,r,o){var n=t.key+"-"+r.name;(o===!1||XM===!1)&&t.registered[n]===void 0&&(t.registered[n]=r.styles)},li=function(t,r,o){ai(t,r,o);var n=t.key+"-"+r.name;if(t.inserted[r.name]===void 0){var s=r;do t.insert(r===s?"."+n:"",s,t.sheet,!0),s=s.next;while(s!==void 0)}}});function AC(e){for(var t=0,r,o=0,n=e.length;n>=4;++o,n-=4)r=e.charCodeAt(o)&255|(e.charCodeAt(++o)&255)<<8|(e.charCodeAt(++o)&255)<<16|(e.charCodeAt(++o)&255)<<24,r=(r&65535)*1540483477+((r>>>16)*59797<<16),r^=r>>>24,t=(r&65535)*1540483477+((r>>>16)*59797<<16)^(t&65535)*1540483477+((t>>>16)*59797<<16);switch(n){case 3:t^=(e.charCodeAt(o+2)&255)<<16;case 2:t^=(e.charCodeAt(o+1)&255)<<8;case 1:t^=e.charCodeAt(o)&255,t=(t&65535)*1540483477+((t>>>16)*59797<<16)}return t^=t>>>13,t=(t&65535)*1540483477+((t>>>16)*59797<<16),((t^t>>>15)>>>0).toString(36)}var zC=et(()=>{});var BC,FC=et(()=>{BC={animationIterationCount:1,aspectRatio:1,borderImageOutset:1,borderImageSlice:1,borderImageWidth:1,boxFlex:1,boxFlexGroup:1,boxOrdinalGroup:1,columnCount:1,columns:1,flex:1,flexGrow:1,flexPositive:1,flexShrink:1,flexNegative:1,flexOrder:1,gridRow:1,gridRowEnd:1,gridRowSpan:1,gridRowStart:1,gridColumn:1,gridColumnEnd:1,gridColumnSpan:1,gridColumnStart:1,msGridRow:1,msGridRowSpan:1,msGridColumn:1,msGridColumnSpan:1,fontWeight:1,lineHeight:1,opacity:1,order:1,orphans:1,scale:1,tabSize:1,widows:1,zIndex:1,zoom:1,WebkitLineClamp:1,fillOpacity:1,floodOpacity:1,stopOpacity:1,strokeDasharray:1,strokeDashoffset:1,strokeMiterlimit:1,strokeOpacity:1,strokeWidth:1}});var qC={};ou(qC,{serializeStyles:()=>kn});function Qp(e,t,r){if(r==null)return"";var o=r;if(o.__emotion_styles!==void 0)return o;switch(typeof r){case"boolean":return"";case"object":{var n=r;if(n.anim===1)return cn={name:n.name,styles:n.styles,next:cn},n.name;var s=r;if(s.styles!==void 0){var i=s.next;if(i!==void 0)for(;i!==void 0;)cn={name:i.name,styles:i.styles,next:cn},i=i.next;var a=s.styles+";";return a}return tI(e,t,r)}case"function":{if(e!==void 0){var l=cn,p=r(e);return cn=l,Qp(e,t,p)}break}}var c=r;if(t==null)return c;var u=t[c];return u!==void 0?u:c}function tI(e,t,r){var o="";if(Array.isArray(r))for(var n=0;n<r.length;n++)o+=Qp(e,t,r[n])+";";else for(var s in r){var i=r[s];if(typeof i!="object"){var a=i;t!=null&&t[a]!==void 0?o+=s+"{"+t[a]+"}":UC(a)&&(o+=Kg(s)+":"+WC(s,a)+";")}else{if(s==="NO_COMPONENT_SELECTOR"&&QM)throw new Error(eI);if(Array.isArray(i)&&typeof i[0]=="string"&&(t==null||t[i[0]]===void 0))for(var l=0;l<i.length;l++)UC(i[l])&&(o+=Kg(s)+":"+WC(s,i[l])+";");else{var p=Qp(e,t,i);switch(s){case"animation":case"animationName":{o+=Kg(s)+":"+p+";";break}default:o+=s+"{"+p+"}"}}}}return o}function kn(e,t,r){if(e.length===1&&typeof e[0]=="object"&&e[0]!==null&&e[0].styles!==void 0)return e[0];var o=!0,n="";cn=void 0;var s=e[0];if(s==null||s.raw===void 0)o=!1,n+=Qp(r,t,s);else{var i=s;n+=i[0]}for(var a=1;a<e.length;a++)if(n+=Qp(r,t,e[a]),o){var l=s;n+=l[a]}VC.lastIndex=0;for(var p="",c;(c=VC.exec(n))!==null;)p+="-"+c[1];var u=AC(n)+p;return{name:u,styles:n,next:cn}}var QM,ZM,JM,HC,UC,Kg,WC,eI,VC,cn,qa=et(()=>{zC();FC();Ld();QM=!1,ZM=/[A-Z]|^ms/g,JM=/_EMO_([^_]+?)_([^]*?)_EMO_/g,HC=function(t){return t.charCodeAt(1)===45},UC=function(t){return t!=null&&typeof t!="boolean"},Kg=Dd(function(e){return HC(e)?e:e.replace(ZM,"-$&").toLowerCase()}),WC=function(t,r){switch(t){case"animation":case"animationName":if(typeof r=="string")return r.replace(JM,function(o,n,s){return cn={name:n,styles:s,next:cn},n})}return BC[t]!==1&&!HC(t)&&typeof r=="number"&&r!==0?r+"px":r},eI="Component selectors can only be used in conjunction with @emotion/babel-plugin, the swc Emotion plugin, or another Emotion-aware compiler transform.";VC=/label:\s*([^\s;{]+)\s*(;|$)/g});var Zp,rI,KC,Ka,Gg,Jp=et(()=>{Zp=P(L()),rI=function(t){return t()},KC=Zp.useInsertionEffect?Zp.useInsertionEffect:!1,Ka=KC||rI,Gg=KC||Zp.useLayoutEffect});function ZC(e){var t=e.displayName||e.name||"Component",r=Ut.forwardRef(function(n,s){var i=Ut.useContext(yo);return Ut.createElement(e,d({theme:i,ref:s},n))});return r.displayName="WithTheme("+t+")",DC(r,e)}var Ut,ec,Yd,Xg,GC,YC,xs,yo,XC,oI,nI,QC,Xd,Yg,JC,sI,iI,e$,Qg=et(()=>{Ut=P(L()),ec=P(L());Ad();J();jd();LC();Xp();qa();Jp();Yd=!1,Xg=Ut.createContext(typeof HTMLElement<"u"?Bg({key:"css"}):null),GC=Xg.Provider,YC=function(){return(0,ec.useContext)(Xg)},xs=function(t){return(0,ec.forwardRef)(function(r,o){var n=(0,ec.useContext)(Xg);return t(r,n,o)})},yo=Ut.createContext({}),XC=function(){return Ut.useContext(yo)},oI=function(t,r){if(typeof r=="function"){var o=r(t);return o}return d({},t,r)},nI=zg(function(e){return zg(function(t){return oI(e,t)})}),QC=function(t){var r=Ut.useContext(yo);return t.theme!==r&&(r=nI(r)(t.theme)),Ut.createElement(yo.Provider,{value:r},t.children)};Xd={}.hasOwnProperty,Yg="__EMOTION_TYPE_PLEASE_DO_NOT_USE__",JC=function(t,r){var o={};for(var n in r)Xd.call(r,n)&&(o[n]=r[n]);return o[Yg]=t,o},sI=function(t){var r=t.cache,o=t.serialized,n=t.isStringTag;return ai(r,o,n),Ka(function(){return li(r,o,n)}),null},iI=xs(function(e,t,r){var o=e.css;typeof o=="string"&&t.registered[o]!==void 0&&(o=t.registered[o]);var n=e[Yg],s=[o],i="";typeof e.className=="string"?i=Ha(t.registered,s,e.className):e.className!=null&&(i=e.className+" ");var a=kn(s,void 0,Ut.useContext(yo));i+=t.key+"-"+a.name;var l={};for(var p in e)Xd.call(e,p)&&p!=="css"&&p!==Yg&&!Yd&&(l[p]=e[p]);return l.className=i,r&&(l.ref=r),Ut.createElement(Ut.Fragment,null,Ut.createElement(sI,{cache:t,serialized:a,isStringTag:typeof n=="string"}),Ut.createElement(n,l))}),e$=iI});var Qd={};ou(Qd,{CacheProvider:()=>GC,ClassNames:()=>dI,Global:()=>aI,ThemeContext:()=>yo,ThemeProvider:()=>QC,__unsafe_useEmotionCache:()=>YC,createElement:()=>Zg,css:()=>t$,jsx:()=>Zg,keyframes:()=>lI,useTheme:()=>XC,withEmotionCache:()=>xs,withTheme:()=>ZC});function t$(){for(var e=arguments.length,t=new Array(e),r=0;r<e;r++)t[r]=arguments[r];return kn(t)}function lI(){var e=t$.apply(void 0,arguments),t="animation-"+e.name;return{name:t,styles:"@keyframes "+t+"{"+e.styles+"}",anim:1,toString:function(){return"_EMO_"+this.name+"_"+this.styles+"_EMO_"}}}function cI(e,t,r){var o=[],n=Ha(e,o,r);return o.length<2?r:n+t(o)}var ho,oV,Zg,aI,pI,uI,dI,tc=et(()=>{Qg();Qg();ho=P(L());Xp();Jp();qa();Ad();J();jd();oV=P(qg()),Zg=function(t,r){var o=arguments;if(r==null||!Xd.call(r,"css"))return ho.createElement.apply(void 0,o);var n=o.length,s=new Array(n);s[0]=e$,s[1]=JC(t,r);for(var i=2;i<n;i++)s[i]=o[i];return ho.createElement.apply(null,s)};(function(e){var t;t||(t=e.JSX||(e.JSX={}))})(Zg||(Zg={}));aI=xs(function(e,t){var r=e.styles,o=kn([r],void 0,ho.useContext(yo)),n=ho.useRef();return Gg(function(){var s=t.key+"-global",i=new t.sheet.constructor({key:s,nonce:t.sheet.nonce,container:t.sheet.container,speedy:t.sheet.isSpeedy}),a=!1,l=document.querySelector('style[data-emotion="'+s+" "+o.name+'"]');return t.sheet.tags.length&&(i.before=t.sheet.tags[0]),l!==null&&(a=!0,l.setAttribute("data-emotion",s),i.hydrate([l])),n.current=[i,a],function(){i.flush()}},[t]),Gg(function(){var s=n.current,i=s[0],a=s[1];if(a){s[1]=!1;return}if(o.next!==void 0&&li(t,o.next,!0),i.tags.length){var l=i.tags[i.tags.length-1].nextElementSibling;i.before=l,i.flush()}t.insert("",o,i,!1)},[t,o.name]),null});pI=function e(t){for(var r=t.length,o=0,n="";o<r;o++){var s=t[o];if(s!=null){var i=void 0;switch(typeof s){case"boolean":break;case"object":{if(Array.isArray(s))i=e(s);else{i="";for(var a in s)s[a]&&a&&(i&&(i+=" "),i+=a)}break}default:i=s}i&&(n&&(n+=" "),n+=i)}}return n};uI=function(t){var r=t.cache,o=t.serializedArr;return Ka(function(){for(var n=0;n<o.length;n++)li(r,o[n],!1)}),null},dI=xs(function(e,t){var r=!1,o=[],n=function(){if(r&&Yd)throw new Error("css can only be used during render");for(var p=arguments.length,c=new Array(p),u=0;u<p;u++)c[u]=arguments[u];var f=kn(c,t.registered);return o.push(f),ai(t,f,!1),t.key+"-"+f.name},s=function(){if(r&&Yd)throw new Error("cx can only be used during render");for(var p=arguments.length,c=new Array(p),u=0;u<p;u++)c[u]=arguments[u];return cI(t.registered,n,pI(c))},i={css:n,cx:s,theme:ho.useContext(yo)},a=e.children(i);return r=!0,ho.createElement(ho.Fragment,null,ho.createElement(uI,{cache:t,serializedArr:o}),a)})});var fI,r$,Jg=et(()=>{Ld();fI=/^((children|dangerouslySetInnerHTML|key|ref|autoFocus|defaultValue|defaultChecked|innerHTML|suppressContentEditableWarning|suppressHydrationWarning|valueLink|abbr|accept|acceptCharset|accessKey|action|allow|allowUserMedia|allowPaymentRequest|allowFullScreen|allowTransparency|alt|async|autoComplete|autoPlay|capture|cellPadding|cellSpacing|challenge|charSet|checked|cite|classID|className|cols|colSpan|content|contentEditable|contextMenu|controls|controlsList|coords|crossOrigin|data|dateTime|decoding|default|defer|dir|disabled|disablePictureInPicture|disableRemotePlayback|download|draggable|encType|enterKeyHint|fetchpriority|fetchPriority|form|formAction|formEncType|formMethod|formNoValidate|formTarget|frameBorder|headers|height|hidden|high|href|hrefLang|htmlFor|httpEquiv|id|inputMode|integrity|is|keyParams|keyType|kind|label|lang|list|loading|loop|low|marginHeight|marginWidth|max|maxLength|media|mediaGroup|method|min|minLength|multiple|muted|name|nonce|noValidate|open|optimum|pattern|placeholder|playsInline|popover|popoverTarget|popoverTargetAction|poster|preload|profile|radioGroup|readOnly|referrerPolicy|rel|required|reversed|role|rows|rowSpan|sandbox|scope|scoped|scrolling|seamless|selected|shape|size|sizes|slot|span|spellCheck|src|srcDoc|srcLang|srcSet|start|step|style|summary|tabIndex|target|title|translate|type|useMap|value|width|wmode|wrap|about|datatype|inlist|prefix|property|resource|typeof|vocab|autoCapitalize|autoCorrect|autoSave|color|incremental|fallback|inert|itemProp|itemScope|itemType|itemID|itemRef|on|option|results|security|unselectable|accentHeight|accumulate|additive|alignmentBaseline|allowReorder|alphabetic|amplitude|arabicForm|ascent|attributeName|attributeType|autoReverse|azimuth|baseFrequency|baselineShift|baseProfile|bbox|begin|bias|by|calcMode|capHeight|clip|clipPathUnits|clipPath|clipRule|colorInterpolation|colorInterpolationFilters|colorProfile|colorRendering|contentScriptType|contentStyleType|cursor|cx|cy|d|decelerate|descent|diffuseConstant|direction|display|divisor|dominantBaseline|dur|dx|dy|edgeMode|elevation|enableBackground|end|exponent|externalResourcesRequired|fill|fillOpacity|fillRule|filter|filterRes|filterUnits|floodColor|floodOpacity|focusable|fontFamily|fontSize|fontSizeAdjust|fontStretch|fontStyle|fontVariant|fontWeight|format|from|fr|fx|fy|g1|g2|glyphName|glyphOrientationHorizontal|glyphOrientationVertical|glyphRef|gradientTransform|gradientUnits|hanging|horizAdvX|horizOriginX|ideographic|imageRendering|in|in2|intercept|k|k1|k2|k3|k4|kernelMatrix|kernelUnitLength|kerning|keyPoints|keySplines|keyTimes|lengthAdjust|letterSpacing|lightingColor|limitingConeAngle|local|markerEnd|markerMid|markerStart|markerHeight|markerUnits|markerWidth|mask|maskContentUnits|maskUnits|mathematical|mode|numOctaves|offset|opacity|operator|order|orient|orientation|origin|overflow|overlinePosition|overlineThickness|panose1|paintOrder|pathLength|patternContentUnits|patternTransform|patternUnits|pointerEvents|points|pointsAtX|pointsAtY|pointsAtZ|preserveAlpha|preserveAspectRatio|primitiveUnits|r|radius|refX|refY|renderingIntent|repeatCount|repeatDur|requiredExtensions|requiredFeatures|restart|result|rotate|rx|ry|scale|seed|shapeRendering|slope|spacing|specularConstant|specularExponent|speed|spreadMethod|startOffset|stdDeviation|stemh|stemv|stitchTiles|stopColor|stopOpacity|strikethroughPosition|strikethroughThickness|string|stroke|strokeDasharray|strokeDashoffset|strokeLinecap|strokeLinejoin|strokeMiterlimit|strokeOpacity|strokeWidth|surfaceScale|systemLanguage|tableValues|targetX|targetY|textAnchor|textDecoration|textRendering|textLength|to|transform|u1|u2|underlinePosition|underlineThickness|unicode|unicodeBidi|unicodeRange|unitsPerEm|vAlphabetic|vHanging|vIdeographic|vMathematical|values|vectorEffect|version|vertAdvY|vertOriginX|vertOriginY|viewBox|viewTarget|visibility|widths|wordSpacing|writingMode|x|xHeight|x1|x2|xChannelSelector|xlinkActuate|xlinkArcrole|xlinkHref|xlinkRole|xlinkShow|xlinkTitle|xlinkType|xmlBase|xmlns|xmlnsXlink|xmlLang|xmlSpace|y|y1|y2|yChannelSelector|z|zoomAndPan|for|class|autofocus)|(([Dd][Aa][Tt][Aa]|[Aa][Rr][Ii][Aa]|x)-.*))$/,r$=Dd(function(e){return fI.test(e)||e.charCodeAt(0)===111&&e.charCodeAt(1)===110&&e.charCodeAt(2)<91})});var Ts,mI,yI,hI,o$,n$,gI,s$,i$=et(()=>{J();tc();qa();Jp();Xp();Ts=P(L());Jg();mI=!1,yI=r$,hI=function(t){return t!=="theme"},o$=function(t){return typeof t=="string"&&t.charCodeAt(0)>96?yI:hI},n$=function(t,r,o){var n;if(r){var s=r.shouldForwardProp;n=t.__emotion_forwardProp&&s?function(i){return t.__emotion_forwardProp(i)&&s(i)}:s}return typeof n!="function"&&o&&(n=t.__emotion_forwardProp),n},gI=function(t){var r=t.cache,o=t.serialized,n=t.isStringTag;return ai(r,o,n),Ka(function(){return li(r,o,n)}),null},s$=function e(t,r){var o=t.__emotion_real===t,n=o&&t.__emotion_base||t,s,i;r!==void 0&&(s=r.label,i=r.target);var a=n$(t,r,o),l=a||o$(n),p=!l("as");return function(){var c=arguments,u=o&&t.__emotion_styles!==void 0?t.__emotion_styles.slice(0):[];if(s!==void 0&&u.push("label:"+s+";"),c[0]==null||c[0].raw===void 0)u.push.apply(u,c);else{var f=c[0];u.push(f[0]);for(var v=c.length,x=1;x<v;x++)u.push(c[x],f[x])}var h=xs(function(b,y,m){var g=p&&b.as||n,T="",w=[],$=b;if(b.theme==null){$={};for(var C in b)$[C]=b[C];$.theme=Ts.useContext(yo)}typeof b.className=="string"?T=Ha(y.registered,w,b.className):b.className!=null&&(T=b.className+" ");var _=kn(u.concat(w),y.registered,$);T+=y.key+"-"+_.name,i!==void 0&&(T+=" "+i);var S=p&&a===void 0?o$(g):l,R={};for(var j in b)p&&j==="as"||S(j)&&(R[j]=b[j]);return R.className=T,m&&(R.ref=m),Ts.createElement(Ts.Fragment,null,Ts.createElement(gI,{cache:y,serialized:_,isStringTag:typeof g=="string"}),Ts.createElement(g,R))});return h.displayName=s!==void 0?s:"Styled("+(typeof n=="string"?n:n.displayName||n.name||"Component")+")",h.defaultProps=t.defaultProps,h.__emotion_real=h,h.__emotion_base=n,h.__emotion_styles=u,h.__emotion_forwardProp=a,Object.defineProperty(h,"toString",{value:function(){return i===void 0&&mI?"NO_COMPONENT_SELECTOR":"."+i}}),h.withComponent=function(b,y){var m=e(b,d({},r,y,{shouldForwardProp:n$(h,y,!0)}));return m.apply(void 0,u)},h}}});var a$={};ou(a$,{default:()=>ev});var xV,vI,ev,l$=et(()=>{i$();J();qa();Jp();Xp();xV=P(L());Jg();vI=["a","abbr","address","area","article","aside","audio","b","base","bdi","bdo","big","blockquote","body","br","button","canvas","caption","cite","code","col","colgroup","data","datalist","dd","del","details","dfn","dialog","div","dl","dt","em","embed","fieldset","figcaption","figure","footer","form","h1","h2","h3","h4","h5","h6","head","header","hgroup","hr","html","i","iframe","img","input","ins","kbd","keygen","label","legend","li","link","main","map","mark","marquee","menu","menuitem","meta","meter","nav","noscript","object","ol","optgroup","option","output","p","param","picture","pre","progress","q","rp","rt","ruby","s","samp","script","section","select","small","source","span","strong","style","sub","summary","sup","table","tbody","td","textarea","tfoot","th","thead","time","title","tr","track","u","ul","var","video","wbr","circle","clipPath","defs","ellipse","foreignObject","g","image","line","linearGradient","mask","path","pattern","polygon","polyline","radialGradient","rect","stop","svg","text","tspan"],ev=s$.bind(null);vI.forEach(function(e){ev[e]=ev(e)})});var c$=se(Zd=>{"use strict";var xI=L(),TI=Symbol.for("react.element"),bI=Symbol.for("react.fragment"),PI=Object.prototype.hasOwnProperty,CI=xI.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,$I={key:!0,ref:!0,__self:!0,__source:!0};function p$(e,t,r){var o,n={},s=null,i=null;r!==void 0&&(s=""+r),t.key!==void 0&&(s=""+t.key),t.ref!==void 0&&(i=t.ref);for(o in t)PI.call(t,o)&&!$I.hasOwnProperty(o)&&(n[o]=t[o]);if(e&&e.defaultProps)for(o in t=e.defaultProps,t)n[o]===void 0&&(n[o]=t[o]);return{$$typeof:TI,type:e,key:s,ref:i,props:n,_owner:CI.current}}Zd.Fragment=bI;Zd.jsx=p$;Zd.jsxs=p$});var H=se((PV,u$)=>{"use strict";u$.exports=c$()});var m$=se(rv=>{"use strict";"use client";var d$=Le();Object.defineProperty(rv,"__esModule",{value:!0});rv.default=OI;var wI=SI(L()),CV=d$(Vp()),_I=(tc(),oa(Qd)),RI=d$((Ad(),oa($C))),EI=H();function f$(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(f$=function(o){return o?r:t})(e)}function SI(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=f$(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}function kI(e,t){let r=(0,RI.default)({key:"css",prepend:e});if(t){let o=r.insert;r.insert=(...n)=>(n[1].styles.match(/^@layer\s+[^{]*$/)||(n[1].styles=`@layer mui {${n[1].styles}}`),o(...n))}return r}var tv=new Map;function OI(e){let{injectFirst:t,enableCssLayer:r,children:o}=e,n=wI.useMemo(()=>{let s=`${t}-${r}`;if(typeof document=="object"&&tv.has(s))return tv.get(s);let i=kI(t,r);return tv.set(s,i),i},[t,r]);return t||r?(0,EI.jsx)(_I.CacheProvider,{value:n,children:o}):o}});var y$=se(ov=>{"use strict";"use client";var NI=Le();Object.defineProperty(ov,"__esModule",{value:!0});Object.defineProperty(ov,"default",{enumerable:!0,get:function(){return MI.default}});var MI=NI(m$())});var g$=se(nv=>{"use strict";"use client";var II=Le();Object.defineProperty(nv,"__esModule",{value:!0});nv.default=zI;var _V=LI(L()),RV=II(Vp()),jI=(tc(),oa(Qd)),DI=H();function h$(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(h$=function(o){return o?r:t})(e)}function LI(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=h$(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}function AI(e){return e==null||Object.keys(e).length===0}function zI(e){let{styles:t,defaultTheme:r={}}=e,o=typeof t=="function"?n=>t(AI(n)?r:n):t;return(0,DI.jsx)(jI.Global,{styles:o})}});var v$=se(sv=>{"use strict";"use client";var BI=Le();Object.defineProperty(sv,"__esModule",{value:!0});Object.defineProperty(sv,"default",{enumerable:!0,get:function(){return FI.default}});var FI=BI(g$())});var On=se(Vo=>{"use strict";"use client";var iv=Le();Object.defineProperty(Vo,"__esModule",{value:!0});Object.defineProperty(Vo,"GlobalStyles",{enumerable:!0,get:function(){return HI.default}});Object.defineProperty(Vo,"StyledEngineProvider",{enumerable:!0,get:function(){return VI.default}});Object.defineProperty(Vo,"ThemeContext",{enumerable:!0,get:function(){return av.ThemeContext}});Object.defineProperty(Vo,"css",{enumerable:!0,get:function(){return av.css}});Vo.default=qI;Vo.internal_processStyles=void 0;Vo.internal_serializeStyles=GI;Object.defineProperty(Vo,"keyframes",{enumerable:!0,get:function(){return av.keyframes}});var UI=iv((l$(),oa(a$))),WI=(qa(),oa(qC)),av=(tc(),oa(Qd)),VI=iv(y$()),HI=iv(v$());function qI(e,t){return(0,UI.default)(e,t)}var KI=(e,t)=>{Array.isArray(e.__emotion_styles)&&(e.__emotion_styles=t(e.__emotion_styles))};Vo.internal_processStyles=KI;var x$=[];function GI(e){return x$[0]=e,(0,WI.serializeStyles)(x$)}});var pi=se((OV,Nn)=>{function lv(){return Nn.exports=lv=Object.assign?Object.assign.bind():function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var o in r)({}).hasOwnProperty.call(r,o)&&(e[o]=r[o])}return e},Nn.exports.__esModule=!0,Nn.exports.default=Nn.exports,lv.apply(null,arguments)}Nn.exports=lv,Nn.exports.__esModule=!0,Nn.exports.default=Nn.exports});var $$=se(Jd=>{"use strict";var YI=Le();Object.defineProperty(Jd,"__esModule",{value:!0});Jd.default=C$;Jd.isPlainObject=ci;var XI=YI(pi()),T$=QI(L());function b$(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(b$=function(o){return o?r:t})(e)}function QI(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=b$(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}function ci(e){if(typeof e!="object"||e===null)return!1;let t=Object.getPrototypeOf(e);return(t===null||t===Object.prototype||Object.getPrototypeOf(t)===null)&&!(Symbol.toStringTag in e)&&!(Symbol.iterator in e)}function P$(e){if(T$.isValidElement(e)||!ci(e))return e;let t={};return Object.keys(e).forEach(r=>{t[r]=P$(e[r])}),t}function C$(e,t,r={clone:!0}){let o=r.clone?(0,XI.default)({},e):e;return ci(e)&&ci(t)&&Object.keys(t).forEach(n=>{T$.isValidElement(t[n])?o[n]=t[n]:ci(t[n])&&Object.prototype.hasOwnProperty.call(e,n)&&ci(e[n])?o[n]=C$(e[n],t[n],r):r.clone?o[n]=ci(t[n])?P$(t[n]):t[n]:o[n]=t[n]}),o}});var Wt=se(Ga=>{"use strict";Object.defineProperty(Ga,"__esModule",{value:!0});var ZI={};Object.defineProperty(Ga,"default",{enumerable:!0,get:function(){return ef.default}});var ef=JI($$());Object.keys(ef).forEach(function(e){e==="default"||e==="__esModule"||Object.prototype.hasOwnProperty.call(ZI,e)||e in Ga&&Ga[e]===ef[e]||Object.defineProperty(Ga,e,{enumerable:!0,get:function(){return ef[e]}})});function w$(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(w$=function(o){return o?r:t})(e)}function JI(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=w$(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}});var O$=se(uv=>{"use strict";var sj=Le();Object.defineProperty(uv,"__esModule",{value:!0});uv.default=aj;var ij=sj(ni());function aj(e){if(typeof e!="string")throw new Error((0,ij.default)(7));return e.charAt(0).toUpperCase()+e.slice(1)}});var ui=se(dv=>{"use strict";var lj=Le();Object.defineProperty(dv,"__esModule",{value:!0});Object.defineProperty(dv,"default",{enumerable:!0,get:function(){return pj.default}});var pj=lj(O$())});var K$=se(We=>{"use strict";var bv=Symbol.for("react.transitional.element"),Pv=Symbol.for("react.portal"),lf=Symbol.for("react.fragment"),pf=Symbol.for("react.strict_mode"),cf=Symbol.for("react.profiler"),uf=Symbol.for("react.consumer"),df=Symbol.for("react.context"),ff=Symbol.for("react.forward_ref"),mf=Symbol.for("react.suspense"),yf=Symbol.for("react.suspense_list"),hf=Symbol.for("react.memo"),gf=Symbol.for("react.lazy"),uD=Symbol.for("react.view_transition"),dD=Symbol.for("react.client.reference");function vo(e){if(typeof e=="object"&&e!==null){var t=e.$$typeof;switch(t){case bv:switch(e=e.type,e){case lf:case cf:case pf:case mf:case yf:case uD:return e;default:switch(e=e&&e.$$typeof,e){case df:case ff:case gf:case hf:return e;case uf:return e;default:return t}}case Pv:return t}}}We.ContextConsumer=uf;We.ContextProvider=df;We.Element=bv;We.ForwardRef=ff;We.Fragment=lf;We.Lazy=gf;We.Memo=hf;We.Portal=Pv;We.Profiler=cf;We.StrictMode=pf;We.Suspense=mf;We.SuspenseList=yf;We.isContextConsumer=function(e){return vo(e)===uf};We.isContextProvider=function(e){return vo(e)===df};We.isElement=function(e){return typeof e=="object"&&e!==null&&e.$$typeof===bv};We.isForwardRef=function(e){return vo(e)===ff};We.isFragment=function(e){return vo(e)===lf};We.isLazy=function(e){return vo(e)===gf};We.isMemo=function(e){return vo(e)===hf};We.isPortal=function(e){return vo(e)===Pv};We.isProfiler=function(e){return vo(e)===cf};We.isStrictMode=function(e){return vo(e)===pf};We.isSuspense=function(e){return vo(e)===mf};We.isSuspenseList=function(e){return vo(e)===yf};We.isValidElementType=function(e){return typeof e=="string"||typeof e=="function"||e===lf||e===cf||e===pf||e===mf||e===yf||typeof e=="object"&&e!==null&&(e.$$typeof===gf||e.$$typeof===hf||e.$$typeof===df||e.$$typeof===uf||e.$$typeof===ff||e.$$typeof===dD||e.getModuleId!==void 0)};We.typeOf=vo});var Y$=se((k7,G$)=>{"use strict";G$.exports=K$()});var ew=se(vf=>{"use strict";Object.defineProperty(vf,"__esModule",{value:!0});vf.default=mD;vf.getFunctionName=Z$;var X$=Y$(),fD=/^\s*function(?:\s|\s*\/\*.*\*\/\s*)+([^(\s/]*)\s*/;function Z$(e){let t=`${e}`.match(fD);return t&&t[1]||""}function J$(e,t=""){return e.displayName||e.name||Z$(e)||t}function Q$(e,t,r){let o=J$(t);return e.displayName||(o!==""?`${r}(${o})`:r)}function mD(e){if(e!=null){if(typeof e=="string")return e;if(typeof e=="function")return J$(e,"Component");if(typeof e=="object")switch(e.$$typeof){case X$.ForwardRef:return Q$(e,e.render,"ForwardRef");case X$.Memo:return Q$(e,e.type,"memo");default:return}}}});var rw=se(Ja=>{"use strict";Object.defineProperty(Ja,"__esModule",{value:!0});var yD={};Object.defineProperty(Ja,"default",{enumerable:!0,get:function(){return xf.default}});var xf=hD(ew());Object.keys(xf).forEach(function(e){e==="default"||e==="__esModule"||Object.prototype.hasOwnProperty.call(yD,e)||e in Ja&&Ja[e]===xf[e]||Object.defineProperty(Ja,e,{enumerable:!0,get:function(){return xf[e]}})});function tw(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(tw=function(o){return o?r:t})(e)}function hD(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=tw(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}});var aw=se($f=>{"use strict";Object.defineProperty($f,"__esModule",{value:!0});$f.default=void 0;function SD(e,t=Number.MIN_SAFE_INTEGER,r=Number.MAX_SAFE_INTEGER){return Math.max(t,Math.min(e,r))}var lH=$f.default=SD});var lw=se(wv=>{"use strict";var kD=Le();Object.defineProperty(wv,"__esModule",{value:!0});Object.defineProperty(wv,"default",{enumerable:!0,get:function(){return OD.default}});var OD=kD(aw())});var cc=se(zf=>{"use strict";var fL=Le();Object.defineProperty(zf,"__esModule",{value:!0});zf.default=void 0;var mL=fL(Wt());function yL(e,t){return t?(0,mL.default)(e,t,{clone:!1}):e}var jG=zf.default=yL});var uc=se(Bf=>{"use strict";var hL=Le();Object.defineProperty(Bf,"__esModule",{value:!0});Bf.default=void 0;var LG=hL(Vp()),gL={},AG=Bf.default=gL});var Pi=se(Po=>{"use strict";var Ff=Le();Object.defineProperty(Po,"__esModule",{value:!0});Po.computeBreakpointsBase=Aw;Po.createEmptyBreakpointObject=Dw;Po.default=void 0;Po.handleBreakpoints=bL;Po.mergeBreakpointsInOrder=CL;Po.removeUnusedBreakpoints=Lw;Po.resolveBreakpointValues=$L;Po.values=void 0;var vL=Ff(pi()),BG=Ff(Vp()),xL=Ff(Wt()),TL=Ff(cc()),jw=Po.values={xs:0,sm:600,md:900,lg:1200,xl:1536},Iv={keys:["xs","sm","md","lg","xl"],up:e=>`@media (min-width:${jw[e]}px)`};function bL(e,t,r){let o=e.theme||{};if(Array.isArray(t)){let s=o.breakpoints||Iv;return t.reduce((i,a,l)=>(i[s.up(s.keys[l])]=r(t[l]),i),{})}if(typeof t=="object"){let s=o.breakpoints||Iv;return Object.keys(t).reduce((i,a)=>{if(Object.keys(s.values||jw).indexOf(a)!==-1){let l=s.up(a);i[l]=r(t[a],a)}else{let l=a;i[l]=t[l]}return i},{})}return r(t)}function PL(e){let t=r=>{let o=r.theme||{},n=e(r),s=o.breakpoints||Iv,i=s.keys.reduce((a,l)=>(r[l]&&(a=a||{},a[s.up(l)]=e((0,vL.default)({theme:o},r[l]))),a),null);return(0,TL.default)(n,i)};return t.propTypes={},t.filterProps=["xs","sm","md","lg","xl",...e.filterProps],t}function Dw(e={}){var t;return((t=e.keys)==null?void 0:t.reduce((o,n)=>{let s=e.up(n);return o[s]={},o},{}))||{}}function Lw(e,t){return e.reduce((r,o)=>{let n=r[o];return(!n||Object.keys(n).length===0)&&delete r[o],r},t)}function CL(e,...t){let r=Dw(e),o=[r,...t].reduce((n,s)=>(0,xL.default)(n,s),{});return Lw(Object.keys(r),o)}function Aw(e,t){if(typeof e!="object")return{};let r={},o=Object.keys(t);return Array.isArray(e)?o.forEach((n,s)=>{s<e.length&&(r[n]=!0)}):o.forEach(n=>{e[n]!=null&&(r[n]=!0)}),r}function $L({values:e,breakpoints:t,base:r}){let o=r||Aw(e,t),n=Object.keys(o);if(n.length===0)return e;let s;return n.reduce((i,a,l)=>(Array.isArray(e)?(i[a]=e[l]!=null?e[l]:e[s],s=l):typeof e=="object"?(i[a]=e[a]!=null?e[a]:e[s],s=a):i[a]=e,i),{})}var FG=Po.default=PL});var Ci=se(sl=>{"use strict";var zw=Le();Object.defineProperty(sl,"__esModule",{value:!0});sl.default=void 0;sl.getPath=Dv;sl.getStyleValue=jv;var wL=zw(ui()),WG=zw(uc()),_L=Pi();function Dv(e,t,r=!0){if(!t||typeof t!="string")return null;if(e&&e.vars&&r){let o=`vars.${t}`.split(".").reduce((n,s)=>n&&n[s]?n[s]:null,e);if(o!=null)return o}return t.split(".").reduce((o,n)=>o&&o[n]!=null?o[n]:null,e)}function jv(e,t,r,o=r){let n;return typeof e=="function"?n=e(r):Array.isArray(e)?n=e[r]||o:n=Dv(e,r)||o,t&&(n=t(n,o,e)),n}function RL(e){let{prop:t,cssProperty:r=e.prop,themeKey:o,transform:n}=e,s=i=>{if(i[t]==null)return null;let a=i[t],l=i.theme,p=Dv(l,o)||{},c=u=>{let f=jv(p,n,u);return u===f&&typeof u=="string"&&(f=jv(p,n,`${t}${u==="default"?"":(0,wL.default)(u)}`,u)),r===!1?f:{[r]:f}};return(0,_L.handleBreakpoints)(i,a,c)};return s.propTypes={},s.filterProps=[t],s}var VG=sl.default=RL});var Bw=se(Lv=>{"use strict";Object.defineProperty(Lv,"__esModule",{value:!0});Lv.default=EL;function EL(e){let t={};return r=>(t[r]===void 0&&(t[r]=e(r)),t[r])}});var dc=se(Br=>{"use strict";var Av=Le();Object.defineProperty(Br,"__esModule",{value:!0});Br.createUnarySpacing=Vw;Br.createUnaryUnit=Ww;Br.default=void 0;Br.getStyleFromPropValue=qw;Br.getValue=Hw;Br.margin=Uv;Br.marginKeys=void 0;Br.padding=Wv;Br.paddingKeys=void 0;var KG=Av(uc()),SL=Pi(),kL=Ci(),OL=Av(cc()),NL=Av(Bw()),ML={m:"margin",p:"padding"},IL={t:"Top",r:"Right",b:"Bottom",l:"Left",x:["Left","Right"],y:["Top","Bottom"]},Fw={marginX:"mx",marginY:"my",paddingX:"px",paddingY:"py"},jL=(0,NL.default)(e=>{if(e.length>2)if(Fw[e])e=Fw[e];else return[e];let[t,r]=e.split(""),o=ML[t],n=IL[r]||"";return Array.isArray(n)?n.map(s=>o+s):[o+n]}),zv=Br.marginKeys=["m","mt","mr","mb","ml","mx","my","margin","marginTop","marginRight","marginBottom","marginLeft","marginX","marginY","marginInline","marginInlineStart","marginInlineEnd","marginBlock","marginBlockStart","marginBlockEnd"],Bv=Br.paddingKeys=["p","pt","pr","pb","pl","px","py","padding","paddingTop","paddingRight","paddingBottom","paddingLeft","paddingX","paddingY","paddingInline","paddingInlineStart","paddingInlineEnd","paddingBlock","paddingBlockStart","paddingBlockEnd"],Uw=[...zv,...Bv];function Ww(e,t,r,o){var n;let s=(n=(0,kL.getPath)(e,t,!1))!=null?n:r;return typeof s=="number"?i=>typeof i=="string"?i:s*i:Array.isArray(s)?i=>typeof i=="string"?i:s[i]:typeof s=="function"?s:()=>{}}function Vw(e){return Ww(e,"spacing",8,"spacing")}function Hw(e,t){if(typeof t=="string"||t==null)return t;let r=Math.abs(t),o=e(r);return t>=0?o:typeof o=="number"?-o:`-${o}`}function qw(e,t){return r=>e.reduce((o,n)=>(o[n]=Hw(t,r),o),{})}function DL(e,t,r,o){if(t.indexOf(r)===-1)return null;let n=jL(r),s=qw(n,o),i=e[r];return(0,SL.handleBreakpoints)(e,i,s)}function Fv(e,t){let r=Vw(e.theme);return Object.keys(e).map(o=>DL(e,t,o,r)).reduce(OL.default,{})}function Uv(e){return Fv(e,zv)}Uv.propTypes={};Uv.filterProps=zv;function Wv(e){return Fv(e,Bv)}Wv.propTypes={};Wv.filterProps=Bv;function Vv(e){return Fv(e,Uw)}Vv.propTypes={};Vv.filterProps=Uw;var GG=Br.default=Vv});var fc=se(Uf=>{"use strict";var LL=Le();Object.defineProperty(Uf,"__esModule",{value:!0});Uf.default=void 0;var AL=LL(cc());function zL(...e){let t=e.reduce((o,n)=>(n.filterProps.forEach(s=>{o[s]=n}),o),{}),r=o=>Object.keys(o).reduce((n,s)=>t[s]?(0,AL.default)(n,t[s](o)):n,{});return r.propTypes={},r.filterProps=e.reduce((o,n)=>o.concat(n.filterProps),[]),r}var XG=Uf.default=zL});var Gw=se(Ne=>{"use strict";var Hv=Le();Object.defineProperty(Ne,"__esModule",{value:!0});Ne.borderTopColor=Ne.borderTop=Ne.borderRightColor=Ne.borderRight=Ne.borderRadius=Ne.borderLeftColor=Ne.borderLeft=Ne.borderColor=Ne.borderBottomColor=Ne.borderBottom=Ne.border=void 0;Ne.borderTransform=$i;Ne.outlineColor=Ne.outline=Ne.default=void 0;var ZG=Hv(uc()),BL=Hv(Ci()),FL=Hv(fc()),Kw=dc(),UL=Pi();function $i(e){return typeof e!="number"?e:`${e}px solid`}function Co(e,t){return(0,BL.default)({prop:e,themeKey:"borders",transform:t})}var WL=Ne.border=Co("border",$i),VL=Ne.borderTop=Co("borderTop",$i),HL=Ne.borderRight=Co("borderRight",$i),qL=Ne.borderBottom=Co("borderBottom",$i),KL=Ne.borderLeft=Co("borderLeft",$i),GL=Ne.borderColor=Co("borderColor"),YL=Ne.borderTopColor=Co("borderTopColor"),XL=Ne.borderRightColor=Co("borderRightColor"),QL=Ne.borderBottomColor=Co("borderBottomColor"),ZL=Ne.borderLeftColor=Co("borderLeftColor"),JL=Ne.outline=Co("outline",$i),e5=Ne.outlineColor=Co("outlineColor"),Wf=e=>{if(e.borderRadius!==void 0&&e.borderRadius!==null){let t=(0,Kw.createUnaryUnit)(e.theme,"shape.borderRadius",4,"borderRadius"),r=o=>({borderRadius:(0,Kw.getValue)(t,o)});return(0,UL.handleBreakpoints)(e,e.borderRadius,r)}return null};Ne.borderRadius=Wf;Wf.propTypes={};Wf.filterProps=["borderRadius"];var t5=(0,FL.default)(WL,VL,HL,qL,KL,GL,YL,XL,QL,ZL,Wf,JL,e5),JG=Ne.default=t5});var Yw=se(Be=>{"use strict";var qv=Le();Object.defineProperty(Be,"__esModule",{value:!0});Be.rowGap=Be.gridTemplateRows=Be.gridTemplateColumns=Be.gridTemplateAreas=Be.gridRow=Be.gridColumn=Be.gridAutoRows=Be.gridAutoFlow=Be.gridAutoColumns=Be.gridArea=Be.gap=Be.default=Be.columnGap=void 0;var Dn=qv(Ci()),r5=qv(fc()),il=dc(),Kv=Pi(),tY=qv(uc()),Vf=e=>{if(e.gap!==void 0&&e.gap!==null){let t=(0,il.createUnaryUnit)(e.theme,"spacing",8,"gap"),r=o=>({gap:(0,il.getValue)(t,o)});return(0,Kv.handleBreakpoints)(e,e.gap,r)}return null};Be.gap=Vf;Vf.propTypes={};Vf.filterProps=["gap"];var Hf=e=>{if(e.columnGap!==void 0&&e.columnGap!==null){let t=(0,il.createUnaryUnit)(e.theme,"spacing",8,"columnGap"),r=o=>({columnGap:(0,il.getValue)(t,o)});return(0,Kv.handleBreakpoints)(e,e.columnGap,r)}return null};Be.columnGap=Hf;Hf.propTypes={};Hf.filterProps=["columnGap"];var qf=e=>{if(e.rowGap!==void 0&&e.rowGap!==null){let t=(0,il.createUnaryUnit)(e.theme,"spacing",8,"rowGap"),r=o=>({rowGap:(0,il.getValue)(t,o)});return(0,Kv.handleBreakpoints)(e,e.rowGap,r)}return null};Be.rowGap=qf;qf.propTypes={};qf.filterProps=["rowGap"];var o5=Be.gridColumn=(0,Dn.default)({prop:"gridColumn"}),n5=Be.gridRow=(0,Dn.default)({prop:"gridRow"}),s5=Be.gridAutoFlow=(0,Dn.default)({prop:"gridAutoFlow"}),i5=Be.gridAutoColumns=(0,Dn.default)({prop:"gridAutoColumns"}),a5=Be.gridAutoRows=(0,Dn.default)({prop:"gridAutoRows"}),l5=Be.gridTemplateColumns=(0,Dn.default)({prop:"gridTemplateColumns"}),p5=Be.gridTemplateRows=(0,Dn.default)({prop:"gridTemplateRows"}),c5=Be.gridTemplateAreas=(0,Dn.default)({prop:"gridTemplateAreas"}),u5=Be.gridArea=(0,Dn.default)({prop:"gridArea"}),d5=(0,r5.default)(Vf,Hf,qf,o5,n5,s5,i5,a5,l5,p5,c5,u5),rY=Be.default=d5});var Qw=se(qo=>{"use strict";var Xw=Le();Object.defineProperty(qo,"__esModule",{value:!0});qo.default=qo.color=qo.bgcolor=qo.backgroundColor=void 0;qo.paletteTransform=Kf;var Gv=Xw(Ci()),f5=Xw(fc());function Kf(e,t){return t==="grey"?t:e}var m5=qo.color=(0,Gv.default)({prop:"color",themeKey:"palette",transform:Kf}),y5=qo.bgcolor=(0,Gv.default)({prop:"bgcolor",cssProperty:"backgroundColor",themeKey:"palette",transform:Kf}),h5=qo.backgroundColor=(0,Gv.default)({prop:"backgroundColor",themeKey:"palette",transform:Kf}),g5=(0,f5.default)(m5,y5,h5),nY=qo.default=g5});var e_=se(ut=>{"use strict";var Jw=Le();Object.defineProperty(ut,"__esModule",{value:!0});ut.sizeWidth=ut.sizeHeight=ut.minWidth=ut.minHeight=ut.maxWidth=ut.maxHeight=ut.height=ut.default=ut.boxSizing=void 0;ut.sizingTransform=Ln;ut.width=void 0;var Es=Jw(Ci()),v5=Jw(fc()),Zw=Pi();function Ln(e){return e<=1&&e!==0?`${e*100}%`:e}var x5=ut.width=(0,Es.default)({prop:"width",transform:Ln}),Yv=e=>{if(e.maxWidth!==void 0&&e.maxWidth!==null){let t=r=>{var o,n;let s=((o=e.theme)==null||(o=o.breakpoints)==null||(o=o.values)==null?void 0:o[r])||Zw.values[r];return s?((n=e.theme)==null||(n=n.breakpoints)==null?void 0:n.unit)!=="px"?{maxWidth:`${s}${e.theme.breakpoints.unit}`}:{maxWidth:s}:{maxWidth:Ln(r)}};return(0,Zw.handleBreakpoints)(e,e.maxWidth,t)}return null};ut.maxWidth=Yv;Yv.filterProps=["maxWidth"];var T5=ut.minWidth=(0,Es.default)({prop:"minWidth",transform:Ln}),b5=ut.height=(0,Es.default)({prop:"height",transform:Ln}),P5=ut.maxHeight=(0,Es.default)({prop:"maxHeight",transform:Ln}),C5=ut.minHeight=(0,Es.default)({prop:"minHeight",transform:Ln}),iY=ut.sizeWidth=(0,Es.default)({prop:"size",cssProperty:"width",transform:Ln}),aY=ut.sizeHeight=(0,Es.default)({prop:"size",cssProperty:"height",transform:Ln}),$5=ut.boxSizing=(0,Es.default)({prop:"boxSizing"}),w5=(0,v5.default)(x5,Yv,T5,b5,P5,C5,$5),lY=ut.default=w5});var mc=se(Gf=>{"use strict";Object.defineProperty(Gf,"__esModule",{value:!0});Gf.default=void 0;var fe=dc(),wi=Gw(),Xv=Yw(),Qv=Qw(),al=e_(),_5={border:{themeKey:"borders",transform:wi.borderTransform},borderTop:{themeKey:"borders",transform:wi.borderTransform},borderRight:{themeKey:"borders",transform:wi.borderTransform},borderBottom:{themeKey:"borders",transform:wi.borderTransform},borderLeft:{themeKey:"borders",transform:wi.borderTransform},borderColor:{themeKey:"palette"},borderTopColor:{themeKey:"palette"},borderRightColor:{themeKey:"palette"},borderBottomColor:{themeKey:"palette"},borderLeftColor:{themeKey:"palette"},outline:{themeKey:"borders",transform:wi.borderTransform},outlineColor:{themeKey:"palette"},borderRadius:{themeKey:"shape.borderRadius",style:wi.borderRadius},color:{themeKey:"palette",transform:Qv.paletteTransform},bgcolor:{themeKey:"palette",cssProperty:"backgroundColor",transform:Qv.paletteTransform},backgroundColor:{themeKey:"palette",transform:Qv.paletteTransform},p:{style:fe.padding},pt:{style:fe.padding},pr:{style:fe.padding},pb:{style:fe.padding},pl:{style:fe.padding},px:{style:fe.padding},py:{style:fe.padding},padding:{style:fe.padding},paddingTop:{style:fe.padding},paddingRight:{style:fe.padding},paddingBottom:{style:fe.padding},paddingLeft:{style:fe.padding},paddingX:{style:fe.padding},paddingY:{style:fe.padding},paddingInline:{style:fe.padding},paddingInlineStart:{style:fe.padding},paddingInlineEnd:{style:fe.padding},paddingBlock:{style:fe.padding},paddingBlockStart:{style:fe.padding},paddingBlockEnd:{style:fe.padding},m:{style:fe.margin},mt:{style:fe.margin},mr:{style:fe.margin},mb:{style:fe.margin},ml:{style:fe.margin},mx:{style:fe.margin},my:{style:fe.margin},margin:{style:fe.margin},marginTop:{style:fe.margin},marginRight:{style:fe.margin},marginBottom:{style:fe.margin},marginLeft:{style:fe.margin},marginX:{style:fe.margin},marginY:{style:fe.margin},marginInline:{style:fe.margin},marginInlineStart:{style:fe.margin},marginInlineEnd:{style:fe.margin},marginBlock:{style:fe.margin},marginBlockStart:{style:fe.margin},marginBlockEnd:{style:fe.margin},displayPrint:{cssProperty:!1,transform:e=>({"@media print":{display:e}})},display:{},overflow:{},textOverflow:{},visibility:{},whiteSpace:{},flexBasis:{},flexDirection:{},flexWrap:{},justifyContent:{},alignItems:{},alignContent:{},order:{},flex:{},flexGrow:{},flexShrink:{},alignSelf:{},justifyItems:{},justifySelf:{},gap:{style:Xv.gap},rowGap:{style:Xv.rowGap},columnGap:{style:Xv.columnGap},gridColumn:{},gridRow:{},gridAutoFlow:{},gridAutoColumns:{},gridAutoRows:{},gridTemplateColumns:{},gridTemplateRows:{},gridTemplateAreas:{},gridArea:{},position:{},zIndex:{themeKey:"zIndex"},top:{},right:{},bottom:{},left:{},boxShadow:{themeKey:"shadows"},width:{transform:al.sizingTransform},maxWidth:{style:al.maxWidth},minWidth:{transform:al.sizingTransform},height:{transform:al.sizingTransform},maxHeight:{transform:al.sizingTransform},minHeight:{transform:al.sizingTransform},boxSizing:{},fontFamily:{themeKey:"typography"},fontSize:{themeKey:"typography"},fontStyle:{themeKey:"typography"},fontWeight:{themeKey:"typography"},letterSpacing:{},textTransform:{},lineHeight:{},textAlign:{},typography:{cssProperty:!1,themeKey:"typography"}},cY=Gf.default=_5});var tx=se(hc=>{"use strict";var ex=Le();Object.defineProperty(hc,"__esModule",{value:!0});hc.default=void 0;hc.unstable_createStyleFunctionSx=t_;var R5=ex(ui()),Zv=ex(cc()),Jv=Ci(),yc=Pi(),E5=ex(mc());function S5(...e){let t=e.reduce((o,n)=>o.concat(Object.keys(n)),[]),r=new Set(t);return e.every(o=>r.size===Object.keys(o).length)}function k5(e,t){return typeof e=="function"?e(t):e}function t_(){function e(r,o,n,s){let i={[r]:o,theme:n},a=s[r];if(!a)return{[r]:o};let{cssProperty:l=r,themeKey:p,transform:c,style:u}=a;if(o==null)return null;if(p==="typography"&&o==="inherit")return{[r]:o};let f=(0,Jv.getPath)(n,p)||{};if(u)return u(i);let v=x=>{let h=(0,Jv.getStyleValue)(f,c,x);return x===h&&typeof x=="string"&&(h=(0,Jv.getStyleValue)(f,c,`${r}${x==="default"?"":(0,R5.default)(x)}`,x)),l===!1?h:{[l]:h}};return(0,yc.handleBreakpoints)(i,o,v)}function t(r){var o;let{sx:n,theme:s={},nested:i}=r||{};if(!n)return null;let a=(o=s.unstable_sxConfig)!=null?o:E5.default;function l(p){let c=p;if(typeof p=="function")c=p(s);else if(typeof p!="object")return p;if(!c)return null;let u=(0,yc.createEmptyBreakpointObject)(s.breakpoints),f=Object.keys(u),v=u;return Object.keys(c).forEach(x=>{let h=k5(c[x],s);if(h!=null)if(typeof h=="object")if(a[x])v=(0,Zv.default)(v,e(x,h,s,a));else{let b=(0,yc.handleBreakpoints)({theme:s},h,y=>({[x]:y}));S5(b,h)?v[x]=t({sx:h,theme:s,nested:!0}):v=(0,Zv.default)(v,b)}else v=(0,Zv.default)(v,e(x,h,s,a))}),!i&&s.modularCssLayers?{"@layer sx":(0,yc.removeUnusedBreakpoints)(f,v)}:(0,yc.removeUnusedBreakpoints)(f,v)}return Array.isArray(n)?n.map(l):l(n)}return t}var r_=t_();r_.filterProps=["sx"];var dY=hc.default=r_});var vc=se((mY,gc)=>{function O5(e,t){if(e==null)return{};var r={};for(var o in e)if({}.hasOwnProperty.call(e,o)){if(t.indexOf(o)!==-1)continue;r[o]=e[o]}return r}gc.exports=O5,gc.exports.__esModule=!0,gc.exports.default=gc.exports});var o_=se(nx=>{"use strict";var ox=Le();Object.defineProperty(nx,"__esModule",{value:!0});nx.default=L5;var rx=ox(pi()),N5=ox(vc()),M5=Wt(),I5=ox(mc()),j5=["sx"],D5=e=>{var t,r;let o={systemProps:{},otherProps:{}},n=(t=e==null||(r=e.theme)==null?void 0:r.unstable_sxConfig)!=null?t:I5.default;return Object.keys(e).forEach(s=>{n[s]?o.systemProps[s]=e[s]:o.otherProps[s]=e[s]}),o};function L5(e){let{sx:t}=e,r=(0,N5.default)(e,j5),{systemProps:o,otherProps:n}=D5(r),s;return Array.isArray(t)?s=[o,...t]:typeof t=="function"?s=(...i)=>{let a=t(...i);return(0,M5.isPlainObject)(a)?(0,rx.default)({},o,a):o}:s=(0,rx.default)({},o,t),(0,rx.default)({},n,{sx:s})}});var Yf=se(ll=>{"use strict";var n_=Le();Object.defineProperty(ll,"__esModule",{value:!0});Object.defineProperty(ll,"default",{enumerable:!0,get:function(){return s_.default}});Object.defineProperty(ll,"extendSxProp",{enumerable:!0,get:function(){return A5.default}});Object.defineProperty(ll,"unstable_createStyleFunctionSx",{enumerable:!0,get:function(){return s_.unstable_createStyleFunctionSx}});Object.defineProperty(ll,"unstable_defaultSxConfig",{enumerable:!0,get:function(){return z5.default}});var s_=B5(tx()),A5=n_(o_()),z5=n_(mc());function i_(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(i_=function(o){return o?r:t})(e)}function B5(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=i_(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}});var sx=se(xc=>{"use strict";var a_=Le();Object.defineProperty(xc,"__esModule",{value:!0});xc.breakpointKeys=void 0;xc.default=V5;var F5=a_(vc()),l_=a_(pi()),U5=["values","unit","step"],gY=xc.breakpointKeys=["xs","sm","md","lg","xl"],W5=e=>{let t=Object.keys(e).map(r=>({key:r,val:e[r]}))||[];return t.sort((r,o)=>r.val-o.val),t.reduce((r,o)=>(0,l_.default)({},r,{[o.key]:o.val}),{})};function V5(e){let{values:t={xs:0,sm:600,md:900,lg:1200,xl:1536},unit:r="px",step:o=5}=e,n=(0,F5.default)(e,U5),s=W5(t),i=Object.keys(s);function a(f){return`@media (min-width:${typeof t[f]=="number"?t[f]:f}${r})`}function l(f){return`@media (max-width:${(typeof t[f]=="number"?t[f]:f)-o/100}${r})`}function p(f,v){let x=i.indexOf(v);return`@media (min-width:${typeof t[f]=="number"?t[f]:f}${r}) and (max-width:${(x!==-1&&typeof t[i[x]]=="number"?t[i[x]]:v)-o/100}${r})`}function c(f){return i.indexOf(f)+1<i.length?p(f,i[i.indexOf(f)+1]):a(f)}function u(f){let v=i.indexOf(f);return v===0?a(i[1]):v===i.length-1?l(i[v]):p(f,i[i.indexOf(f)+1]).replace("@media","@media not all and")}return(0,l_.default)({keys:i,values:s,up:a,down:l,between:p,only:c,not:u,unit:r},n)}});var p_=se(Xf=>{"use strict";Object.defineProperty(Xf,"__esModule",{value:!0});Xf.default=void 0;var H5={borderRadius:4},xY=Xf.default=H5});var c_=se(ix=>{"use strict";Object.defineProperty(ix,"__esModule",{value:!0});ix.default=K5;var q5=dc();function K5(e=8){if(e.mui)return e;let t=(0,q5.createUnarySpacing)({spacing:e}),r=(...o)=>(o.length===0?[1]:o).map(s=>{let i=t(s);return typeof i=="number"?`${i}px`:i}).join(" ");return r.mui=!0,r}});var lx=se(ax=>{"use strict";Object.defineProperty(ax,"__esModule",{value:!0});ax.default=G5;function G5(e,t){let r=this;return r.vars&&typeof r.getColorSchemeSelector=="function"?{[r.getColorSchemeSelector(e).replace(/(\[[^\]]+\])/,"*:where($1)")]:t}:r.palette.mode===e?t:{}}});var d_=se(Qf=>{"use strict";var An=Le();Object.defineProperty(Qf,"__esModule",{value:!0});Qf.default=void 0;var px=An(pi()),Y5=An(vc()),u_=An(Wt()),X5=An(sx()),Q5=An(p_()),Z5=An(c_()),J5=An(tx()),e4=An(mc()),t4=An(lx()),r4=["breakpoints","palette","spacing","shape"];function o4(e={},...t){let{breakpoints:r={},palette:o={},spacing:n,shape:s={}}=e,i=(0,Y5.default)(e,r4),a=(0,X5.default)(r),l=(0,Z5.default)(n),p=(0,u_.default)({breakpoints:a,direction:"ltr",components:{},palette:(0,px.default)({mode:"light"},o),spacing:l,shape:(0,px.default)({},Q5.default,s)},i);return p.applyStyles=t4.default,p=t.reduce((c,u)=>(0,u_.default)(c,u),p),p.unstable_sxConfig=(0,px.default)({},e4.default,i?.unstable_sxConfig),p.unstable_sx=function(u){return(0,J5.default)({sx:u,theme:this})},p}var CY=Qf.default=o4});var ux=se(Tc=>{"use strict";var cx=Le();Object.defineProperty(Tc,"__esModule",{value:!0});Object.defineProperty(Tc,"default",{enumerable:!0,get:function(){return n4.default}});Object.defineProperty(Tc,"private_createBreakpoints",{enumerable:!0,get:function(){return s4.default}});Object.defineProperty(Tc,"unstable_applyStyles",{enumerable:!0,get:function(){return i4.default}});var n4=cx(d_()),s4=cx(sx()),i4=cx(lx())});var $r=se(ht=>{"use strict";var m_=Le();Object.defineProperty(ht,"__esModule",{value:!0});ht.alpha=v_;ht.blend=h4;ht.colorChannel=void 0;ht.darken=mx;ht.decomposeColor=$o;ht.emphasize=x_;ht.getContrastRatio=u4;ht.getLuminance=Zf;ht.hexToRgb=y_;ht.hslToRgb=g_;ht.lighten=yx;ht.private_safeAlpha=d4;ht.private_safeColorChannel=void 0;ht.private_safeDarken=f4;ht.private_safeEmphasize=y4;ht.private_safeLighten=m4;ht.recomposeColor=pl;ht.rgbToHex=c4;var f_=m_(ni()),a4=m_(lw());function fx(e,t=0,r=1){return(0,a4.default)(e,t,r)}function y_(e){e=e.slice(1);let t=new RegExp(`.{1,${e.length>=6?2:1}}`,"g"),r=e.match(t);return r&&r[0].length===1&&(r=r.map(o=>o+o)),r?`rgb${r.length===4?"a":""}(${r.map((o,n)=>n<3?parseInt(o,16):Math.round(parseInt(o,16)/255*1e3)/1e3).join(", ")})`:""}function l4(e){let t=e.toString(16);return t.length===1?`0${t}`:t}function $o(e){if(e.type)return e;if(e.charAt(0)==="#")return $o(y_(e));let t=e.indexOf("("),r=e.substring(0,t);if(["rgb","rgba","hsl","hsla","color"].indexOf(r)===-1)throw new Error((0,f_.default)(9,e));let o=e.substring(t+1,e.length-1),n;if(r==="color"){if(o=o.split(" "),n=o.shift(),o.length===4&&o[3].charAt(0)==="/"&&(o[3]=o[3].slice(1)),["srgb","display-p3","a98-rgb","prophoto-rgb","rec-2020"].indexOf(n)===-1)throw new Error((0,f_.default)(10,n))}else o=o.split(",");return o=o.map(s=>parseFloat(s)),{type:r,values:o,colorSpace:n}}var h_=e=>{let t=$o(e);return t.values.slice(0,3).map((r,o)=>t.type.indexOf("hsl")!==-1&&o!==0?`${r}%`:r).join(" ")};ht.colorChannel=h_;var p4=(e,t)=>{try{return h_(e)}catch{return e}};ht.private_safeColorChannel=p4;function pl(e){let{type:t,colorSpace:r}=e,{values:o}=e;return t.indexOf("rgb")!==-1?o=o.map((n,s)=>s<3?parseInt(n,10):n):t.indexOf("hsl")!==-1&&(o[1]=`${o[1]}%`,o[2]=`${o[2]}%`),t.indexOf("color")!==-1?o=`${r} ${o.join(" ")}`:o=`${o.join(", ")}`,`${t}(${o})`}function c4(e){if(e.indexOf("#")===0)return e;let{values:t}=$o(e);return`#${t.map((r,o)=>l4(o===3?Math.round(255*r):r)).join("")}`}function g_(e){e=$o(e);let{values:t}=e,r=t[0],o=t[1]/100,n=t[2]/100,s=o*Math.min(n,1-n),i=(p,c=(p+r/30)%12)=>n-s*Math.max(Math.min(c-3,9-c,1),-1),a="rgb",l=[Math.round(i(0)*255),Math.round(i(8)*255),Math.round(i(4)*255)];return e.type==="hsla"&&(a+="a",l.push(t[3])),pl({type:a,values:l})}function Zf(e){e=$o(e);let t=e.type==="hsl"||e.type==="hsla"?$o(g_(e)).values:e.values;return t=t.map(r=>(e.type!=="color"&&(r/=255),r<=.03928?r/12.92:((r+.055)/1.055)**2.4)),Number((.2126*t[0]+.7152*t[1]+.0722*t[2]).toFixed(3))}function u4(e,t){let r=Zf(e),o=Zf(t);return(Math.max(r,o)+.05)/(Math.min(r,o)+.05)}function v_(e,t){return e=$o(e),t=fx(t),(e.type==="rgb"||e.type==="hsl")&&(e.type+="a"),e.type==="color"?e.values[3]=`/${t}`:e.values[3]=t,pl(e)}function d4(e,t,r){try{return v_(e,t)}catch{return e}}function mx(e,t){if(e=$o(e),t=fx(t),e.type.indexOf("hsl")!==-1)e.values[2]*=1-t;else if(e.type.indexOf("rgb")!==-1||e.type.indexOf("color")!==-1)for(let r=0;r<3;r+=1)e.values[r]*=1-t;return pl(e)}function f4(e,t,r){try{return mx(e,t)}catch{return e}}function yx(e,t){if(e=$o(e),t=fx(t),e.type.indexOf("hsl")!==-1)e.values[2]+=(100-e.values[2])*t;else if(e.type.indexOf("rgb")!==-1)for(let r=0;r<3;r+=1)e.values[r]+=(255-e.values[r])*t;else if(e.type.indexOf("color")!==-1)for(let r=0;r<3;r+=1)e.values[r]+=(1-e.values[r])*t;return pl(e)}function m4(e,t,r){try{return yx(e,t)}catch{return e}}function x_(e,t=.15){return Zf(e)>.5?mx(e,t):yx(e,t)}function y4(e,t,r){try{return x_(e,t)}catch{return e}}function h4(e,t,r,o=1){let n=(l,p)=>Math.round((l**(1/o)*(1-r)+p**(1/o)*r)**o),s=$o(e),i=$o(t),a=[n(s.values[0],i.values[0]),n(s.values[1],i.values[1]),n(s.values[2],i.values[2])];return pl({type:"rgb",values:a})}});var I_=se(yl=>{"use strict";var ml=Le();Object.defineProperty(yl,"__esModule",{value:!0});yl.default=tA;yl.shouldForwardProp=rm;yl.systemDefaultTheme=void 0;var wo=ml(pi()),bx=ml(vc()),nm=Y4(On()),W4=Wt(),fX=ml(ui()),mX=ml(rw()),V4=ml(ux()),H4=ml(Yf()),q4=["ownerState"],K4=["variants"],G4=["name","slot","skipVariantsResolver","skipSx","overridesResolver"];function M_(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(M_=function(o){return o?r:t})(e)}function Y4(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=M_(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}function X4(e){return Object.keys(e).length===0}function Q4(e){return typeof e=="string"&&e.charCodeAt(0)>96}function rm(e){return e!=="ownerState"&&e!=="theme"&&e!=="sx"&&e!=="as"}function N_(e,t){return t&&e&&typeof e=="object"&&e.styles&&!e.styles.startsWith("@layer")&&(e.styles=`@layer ${t}{${String(e.styles)}}`),e}var Z4=yl.systemDefaultTheme=(0,V4.default)(),J4=e=>e&&e.charAt(0).toLowerCase()+e.slice(1);function tm({defaultTheme:e,theme:t,themeId:r}){return X4(t)?e:t[r]||t}function eA(e){return e?(t,r)=>r[e]:null}function om(e,t,r){let{ownerState:o}=t,n=(0,bx.default)(t,q4),s=typeof e=="function"?e((0,wo.default)({ownerState:o},n)):e;if(Array.isArray(s))return s.flatMap(i=>om(i,(0,wo.default)({ownerState:o},n),r));if(s&&typeof s=="object"&&Array.isArray(s.variants)){let{variants:i=[]}=s,l=(0,bx.default)(s,K4);return i.forEach(p=>{let c=!0;if(typeof p.props=="function"?c=p.props((0,wo.default)({ownerState:o},n,o)):Object.keys(p.props).forEach(u=>{o?.[u]!==p.props[u]&&n[u]!==p.props[u]&&(c=!1)}),c){Array.isArray(l)||(l=[l]);let u=typeof p.style=="function"?p.style((0,wo.default)({ownerState:o},n,o)):p.style;l.push(r?N_((0,nm.internal_serializeStyles)(u),r):u)}}),l}return r?N_((0,nm.internal_serializeStyles)(s),r):s}function tA(e={}){let{themeId:t,defaultTheme:r=Z4,rootShouldForwardProp:o=rm,slotShouldForwardProp:n=rm}=e,s=i=>(0,H4.default)((0,wo.default)({},i,{theme:tm((0,wo.default)({},i,{defaultTheme:r,themeId:t}))}));return s.__mui_systemSx=!0,(i,a={})=>{(0,nm.internal_processStyles)(i,$=>$.filter(C=>!(C!=null&&C.__mui_systemSx)));let{name:l,slot:p,skipVariantsResolver:c,skipSx:u,overridesResolver:f=eA(J4(p))}=a,v=(0,bx.default)(a,G4),x=l&&l.startsWith("Mui")||p?"components":"custom",h=c!==void 0?c:p&&p!=="Root"&&p!=="root"||!1,b=u||!1,y,m=rm;p==="Root"||p==="root"?m=o:p?m=n:Q4(i)&&(m=void 0);let g=(0,nm.default)(i,(0,wo.default)({shouldForwardProp:m,label:y},v)),T=$=>typeof $=="function"&&$.__emotion_real!==$||(0,W4.isPlainObject)($)?C=>{let _=tm({theme:C.theme,defaultTheme:r,themeId:t});return om($,(0,wo.default)({},C,{theme:_}),_.modularCssLayers?x:void 0)}:$,w=($,...C)=>{let _=T($),S=C?C.map(T):[];l&&f&&S.push(U=>{let z=tm((0,wo.default)({},U,{defaultTheme:r,themeId:t}));if(!z.components||!z.components[l]||!z.components[l].styleOverrides)return null;let Z=z.components[l].styleOverrides,B={};return Object.entries(Z).forEach(([D,q])=>{B[D]=om(q,(0,wo.default)({},U,{theme:z}),z.modularCssLayers?"theme":void 0)}),f(U,B)}),l&&!h&&S.push(U=>{var z;let Z=tm((0,wo.default)({},U,{defaultTheme:r,themeId:t})),B=Z==null||(z=Z.components)==null||(z=z[l])==null?void 0:z.variants;return om({variants:B},(0,wo.default)({},U,{theme:Z}),Z.modularCssLayers?"theme":void 0)}),b||S.push(s);let R=S.length-C.length;if(Array.isArray($)&&R>0){let U=new Array(R).fill("");_=[...$,...U],_.raw=[...$.raw,...U]}let j=g(_,...S);return i.muiName&&(j.muiName=i.muiName),j};return g.withConfig&&(w.withConfig=g.withConfig),w}}});var Hk=se(Qm=>{"use strict";"use client";Object.defineProperty(Qm,"__esModule",{value:!0});Qm.default=void 0;var T6=P6(L()),b6=On();function Vk(e){if(typeof WeakMap!="function")return null;var t=new WeakMap,r=new WeakMap;return(Vk=function(o){return o?r:t})(e)}function P6(e,t){if(!t&&e&&e.__esModule)return e;if(e===null||typeof e!="object"&&typeof e!="function")return{default:e};var r=Vk(t);if(r&&r.has(e))return r.get(e);var o={__proto__:null},n=Object.defineProperty&&Object.getOwnPropertyDescriptor;for(var s in e)if(s!=="default"&&Object.prototype.hasOwnProperty.call(e,s)){var i=n?Object.getOwnPropertyDescriptor(e,s):null;i&&(i.get||i.set)?Object.defineProperty(o,s,i):o[s]=e[s]}return o.default=e,r&&r.set(e,o),o}function C6(e){return Object.keys(e).length===0}function $6(e=null){let t=T6.useContext(b6.ThemeContext);return!t||C6(t)?e:t}var lge=Qm.default=$6});var Q=P(L()),UT=P(z1());var F1=function(e,t,r,o){var n;t[0]=0;for(var s=1;s<t.length;s++){var i=t[s++],a=t[s]?(t[0]|=i?1:2,r[t[s++]]):t[++s];i===3?o[0]=a:i===4?o[1]=Object.assign(o[1]||{},a):i===5?(o[1]=o[1]||{})[t[++s]]=a:i===6?o[1][t[++s]]+=a+"":i?(n=e.apply(a,F1(e,a,r,["",null])),o.push(n),a[0]?t[0]|=2:(t[s-2]=0,t[s]=n)):o.push(a)}return o},B1=new Map;function U1(e){var t=B1.get(this);return t||(t=new Map,B1.set(this,t)),(t=F1(this,t.get(e)||(t.set(e,t=(function(r){for(var o,n,s=1,i="",a="",l=[0],p=function(f){s===1&&(f||(i=i.replace(/^\s*\n\s*|\s*\n\s*$/g,"")))?l.push(0,f,i):s===3&&(f||i)?(l.push(3,f,i),s=2):s===2&&i==="..."&&f?l.push(4,f,0):s===2&&i&&!f?l.push(5,0,!0,i):s>=5&&((i||!f&&s===5)&&(l.push(s,0,i,n),s=6),f&&(l.push(s,f,0,n),s=6)),i=""},c=0;c<r.length;c++){c&&(s===1&&p(),p(c));for(var u=0;u<r[c].length;u++)o=r[c][u],s===1?o==="<"?(p(),l=[l],s=3):i+=o:s===4?i==="--"&&o===">"?(s=1,i=""):i=o+i[0]:a?o===a?a="":i+=o:o==='"'||o==="'"?a=o:o===">"?(p(),s=1):s&&(o==="="?(s=5,n=i,i=""):o==="/"&&(s<5||r[c][u+1]===">")?(p(),s===3&&(l=l[0]),s=l,(l=l[0]).push(2,0,s),s=0):o===" "||o==="	"||o===`
`||o==="\r"?(p(),s=2):i+=o),s===3&&i==="!--"&&(s=4,l=l[0])}return p(),l})(e)),t),arguments,[])).length>1?t:t[0]}J();function k(e,t){if(e==null)return{};var r={};for(var o in e)if({}.hasOwnProperty.call(e,o)){if(t.indexOf(o)!==-1)continue;r[o]=e[o]}return r}var OG=P(L());var bt=P(On());var Q9=P(L());var sf=P(On());J();var xv=P(Wt());J();var ej=["values","unit","step"];var tj=e=>{let t=Object.keys(e).map(r=>({key:r,val:e[r]}))||[];return t.sort((r,o)=>r.val-o.val),t.reduce((r,o)=>d({},r,{[o.key]:o.val}),{})};function pv(e){let{values:t={xs:0,sm:600,md:900,lg:1200,xl:1536},unit:r="px",step:o=5}=e,n=k(e,ej),s=tj(t),i=Object.keys(s);function a(f){return`@media (min-width:${typeof t[f]=="number"?t[f]:f}${r})`}function l(f){return`@media (max-width:${(typeof t[f]=="number"?t[f]:f)-o/100}${r})`}function p(f,v){let x=i.indexOf(v);return`@media (min-width:${typeof t[f]=="number"?t[f]:f}${r}) and (max-width:${(x!==-1&&typeof t[i[x]]=="number"?t[i[x]]:v)-o/100}${r})`}function c(f){return i.indexOf(f)+1<i.length?p(f,i[i.indexOf(f)+1]):a(f)}function u(f){let v=i.indexOf(f);return v===0?a(i[1]):v===i.length-1?l(i[v]):p(f,i[i.indexOf(f)+1]).replace("@media","@media not all and")}return d({keys:i,values:s,up:a,down:l,between:p,only:c,not:u,unit:r},n)}var rj={borderRadius:4},_$=rj;J();var S$=P(Wt());var R$=P(Wt());function oj(e,t){return t?(0,R$.default)(e,t,{clone:!1}):e}var bs=oj;var tf={xs:0,sm:600,md:900,lg:1200,xl:1536},E$={keys:["xs","sm","md","lg","xl"],up:e=>`@media (min-width:${tf[e]}px)`};function Vt(e,t,r){let o=e.theme||{};if(Array.isArray(t)){let s=o.breakpoints||E$;return t.reduce((i,a,l)=>(i[s.up(s.keys[l])]=r(t[l]),i),{})}if(typeof t=="object"){let s=o.breakpoints||E$;return Object.keys(t).reduce((i,a)=>{if(Object.keys(s.values||tf).indexOf(a)!==-1){let l=s.up(a);i[l]=r(t[a],a)}else{let l=a;i[l]=t[l]}return i},{})}return r(t)}function cv(e={}){var t;return((t=e.keys)==null?void 0:t.reduce((o,n)=>{let s=e.up(n);return o[s]={},o},{}))||{}}function rf(e,t){return e.reduce((r,o)=>{let n=r[o];return(!n||Object.keys(n).length===0)&&delete r[o],r},t)}function k$(e,...t){let r=cv(e),o=[r,...t].reduce((n,s)=>(0,S$.default)(n,s),{});return rf(Object.keys(r),o)}function nj(e,t){if(typeof e!="object")return{};let r={},o=Object.keys(t);return Array.isArray(e)?o.forEach((n,s)=>{s<e.length&&(r[n]=!0)}):o.forEach(n=>{e[n]!=null&&(r[n]=!0)}),r}function of({values:e,breakpoints:t,base:r}){let o=r||nj(e,t),n=Object.keys(o);if(n.length===0)return e;let s;return n.reduce((i,a,l)=>(Array.isArray(e)?(i[a]=e[l]!=null?e[l]:e[s],s=l):typeof e=="object"?(i[a]=e[a]!=null?e[a]:e[s],s=a):i[a]=e,i),{})}var N$=P(ui());function Ya(e,t,r=!0){if(!t||typeof t!="string")return null;if(e&&e.vars&&r){let o=`vars.${t}`.split(".").reduce((n,s)=>n&&n[s]?n[s]:null,e);if(o!=null)return o}return t.split(".").reduce((o,n)=>o&&o[n]!=null?o[n]:null,e)}function rc(e,t,r,o=r){let n;return typeof e=="function"?n=e(r):Array.isArray(e)?n=e[r]||o:n=Ya(e,r)||o,t&&(n=t(n,o,e)),n}function cj(e){let{prop:t,cssProperty:r=e.prop,themeKey:o,transform:n}=e,s=i=>{if(i[t]==null)return null;let a=i[t],l=i.theme,p=Ya(l,o)||{};return Vt(i,a,u=>{let f=rc(p,n,u);return u===f&&typeof u=="string"&&(f=rc(p,n,`${t}${u==="default"?"":(0,N$.default)(u)}`,u)),r===!1?f:{[r]:f}})};return s.propTypes={},s.filterProps=[t],s}var Xe=cj;function fv(e){let t={};return r=>(t[r]===void 0&&(t[r]=e(r)),t[r])}var uj={m:"margin",p:"padding"},dj={t:"Top",r:"Right",b:"Bottom",l:"Left",x:["Left","Right"],y:["Top","Bottom"]},M$={marginX:"mx",marginY:"my",paddingX:"px",paddingY:"py"},fj=fv(e=>{if(e.length>2)if(M$[e])e=M$[e];else return[e];let[t,r]=e.split(""),o=uj[t],n=dj[r]||"";return Array.isArray(n)?n.map(s=>o+s):[o+n]}),mv=["m","mt","mr","mb","ml","mx","my","margin","marginTop","marginRight","marginBottom","marginLeft","marginX","marginY","marginInline","marginInlineStart","marginInlineEnd","marginBlock","marginBlockStart","marginBlockEnd"],yv=["p","pt","pr","pb","pl","px","py","padding","paddingTop","paddingRight","paddingBottom","paddingLeft","paddingX","paddingY","paddingInline","paddingInlineStart","paddingInlineEnd","paddingBlock","paddingBlockStart","paddingBlockEnd"],I$=[...mv,...yv];function di(e,t,r,o){var n;let s=(n=Ya(e,t,!1))!=null?n:r;return typeof s=="number"?i=>typeof i=="string"?i:s*i:Array.isArray(s)?i=>typeof i=="string"?i:s[i]:typeof s=="function"?s:()=>{}}function oc(e){return di(e,"spacing",8,"spacing")}function un(e,t){if(typeof t=="string"||t==null)return t;let r=Math.abs(t),o=e(r);return t>=0?o:typeof o=="number"?-o:`-${o}`}function mj(e,t){return r=>e.reduce((o,n)=>(o[n]=un(t,r),o),{})}function yj(e,t,r,o){if(t.indexOf(r)===-1)return null;let n=fj(r),s=mj(n,o),i=e[r];return Vt(e,i,s)}function hv(e,t){let r=oc(e.theme);return Object.keys(e).map(o=>yj(e,t,o,r)).reduce(bs,{})}function pt(e){return hv(e,mv)}pt.propTypes={};pt.filterProps=mv;function ct(e){return hv(e,yv)}ct.propTypes={};ct.filterProps=yv;function j$(e){return hv(e,I$)}j$.propTypes={};j$.filterProps=I$;function gv(e=8){if(e.mui)return e;let t=oc({spacing:e}),r=(...o)=>(o.length===0?[1]:o).map(s=>{let i=t(s);return typeof i=="number"?`${i}px`:i}).join(" ");return r.mui=!0,r}var D$=P(ui());function hj(...e){let t=e.reduce((o,n)=>(n.filterProps.forEach(s=>{o[s]=n}),o),{}),r=o=>Object.keys(o).reduce((n,s)=>t[s]?bs(n,t[s](o)):n,{});return r.propTypes={},r.filterProps=e.reduce((o,n)=>o.concat(n.filterProps),[]),r}var Ps=hj;function eo(e){return typeof e!="number"?e:`${e}px solid`}function go(e,t){return Xe({prop:e,themeKey:"borders",transform:t})}var gj=go("border",eo),vj=go("borderTop",eo),xj=go("borderRight",eo),Tj=go("borderBottom",eo),bj=go("borderLeft",eo),Pj=go("borderColor"),Cj=go("borderTopColor"),$j=go("borderRightColor"),wj=go("borderBottomColor"),_j=go("borderLeftColor"),Rj=go("outline",eo),Ej=go("outlineColor"),nc=e=>{if(e.borderRadius!==void 0&&e.borderRadius!==null){let t=di(e.theme,"shape.borderRadius",4,"borderRadius"),r=o=>({borderRadius:un(t,o)});return Vt(e,e.borderRadius,r)}return null};nc.propTypes={};nc.filterProps=["borderRadius"];var s9=Ps(gj,vj,xj,Tj,bj,Pj,Cj,$j,wj,_j,nc,Rj,Ej);var sc=e=>{if(e.gap!==void 0&&e.gap!==null){let t=di(e.theme,"spacing",8,"gap"),r=o=>({gap:un(t,o)});return Vt(e,e.gap,r)}return null};sc.propTypes={};sc.filterProps=["gap"];var ic=e=>{if(e.columnGap!==void 0&&e.columnGap!==null){let t=di(e.theme,"spacing",8,"columnGap"),r=o=>({columnGap:un(t,o)});return Vt(e,e.columnGap,r)}return null};ic.propTypes={};ic.filterProps=["columnGap"];var ac=e=>{if(e.rowGap!==void 0&&e.rowGap!==null){let t=di(e.theme,"spacing",8,"rowGap"),r=o=>({rowGap:un(t,o)});return Vt(e,e.rowGap,r)}return null};ac.propTypes={};ac.filterProps=["rowGap"];var Sj=Xe({prop:"gridColumn"}),kj=Xe({prop:"gridRow"}),Oj=Xe({prop:"gridAutoFlow"}),Nj=Xe({prop:"gridAutoColumns"}),Mj=Xe({prop:"gridAutoRows"}),Ij=Xe({prop:"gridTemplateColumns"}),jj=Xe({prop:"gridTemplateRows"}),Dj=Xe({prop:"gridTemplateAreas"}),Lj=Xe({prop:"gridArea"}),u9=Ps(sc,ic,ac,Sj,kj,Oj,Nj,Mj,Ij,jj,Dj,Lj);function fi(e,t){return t==="grey"?t:e}var Aj=Xe({prop:"color",themeKey:"palette",transform:fi}),zj=Xe({prop:"bgcolor",cssProperty:"backgroundColor",themeKey:"palette",transform:fi}),Bj=Xe({prop:"backgroundColor",themeKey:"palette",transform:fi}),y9=Ps(Aj,zj,Bj);function Lr(e){return e<=1&&e!==0?`${e*100}%`:e}var Fj=Xe({prop:"width",transform:Lr}),nf=e=>{if(e.maxWidth!==void 0&&e.maxWidth!==null){let t=r=>{var o,n;let s=((o=e.theme)==null||(o=o.breakpoints)==null||(o=o.values)==null?void 0:o[r])||tf[r];return s?((n=e.theme)==null||(n=n.breakpoints)==null?void 0:n.unit)!=="px"?{maxWidth:`${s}${e.theme.breakpoints.unit}`}:{maxWidth:s}:{maxWidth:Lr(r)}};return Vt(e,e.maxWidth,t)}return null};nf.filterProps=["maxWidth"];var Uj=Xe({prop:"minWidth",transform:Lr}),Wj=Xe({prop:"height",transform:Lr}),Vj=Xe({prop:"maxHeight",transform:Lr}),Hj=Xe({prop:"minHeight",transform:Lr}),T9=Xe({prop:"size",cssProperty:"width",transform:Lr}),b9=Xe({prop:"size",cssProperty:"height",transform:Lr}),qj=Xe({prop:"boxSizing"}),P9=Ps(Fj,nf,Uj,Wj,Vj,Hj,qj);var Kj={border:{themeKey:"borders",transform:eo},borderTop:{themeKey:"borders",transform:eo},borderRight:{themeKey:"borders",transform:eo},borderBottom:{themeKey:"borders",transform:eo},borderLeft:{themeKey:"borders",transform:eo},borderColor:{themeKey:"palette"},borderTopColor:{themeKey:"palette"},borderRightColor:{themeKey:"palette"},borderBottomColor:{themeKey:"palette"},borderLeftColor:{themeKey:"palette"},outline:{themeKey:"borders",transform:eo},outlineColor:{themeKey:"palette"},borderRadius:{themeKey:"shape.borderRadius",style:nc},color:{themeKey:"palette",transform:fi},bgcolor:{themeKey:"palette",cssProperty:"backgroundColor",transform:fi},backgroundColor:{themeKey:"palette",transform:fi},p:{style:ct},pt:{style:ct},pr:{style:ct},pb:{style:ct},pl:{style:ct},px:{style:ct},py:{style:ct},padding:{style:ct},paddingTop:{style:ct},paddingRight:{style:ct},paddingBottom:{style:ct},paddingLeft:{style:ct},paddingX:{style:ct},paddingY:{style:ct},paddingInline:{style:ct},paddingInlineStart:{style:ct},paddingInlineEnd:{style:ct},paddingBlock:{style:ct},paddingBlockStart:{style:ct},paddingBlockEnd:{style:ct},m:{style:pt},mt:{style:pt},mr:{style:pt},mb:{style:pt},ml:{style:pt},mx:{style:pt},my:{style:pt},margin:{style:pt},marginTop:{style:pt},marginRight:{style:pt},marginBottom:{style:pt},marginLeft:{style:pt},marginX:{style:pt},marginY:{style:pt},marginInline:{style:pt},marginInlineStart:{style:pt},marginInlineEnd:{style:pt},marginBlock:{style:pt},marginBlockStart:{style:pt},marginBlockEnd:{style:pt},displayPrint:{cssProperty:!1,transform:e=>({"@media print":{display:e}})},display:{},overflow:{},textOverflow:{},visibility:{},whiteSpace:{},flexBasis:{},flexDirection:{},flexWrap:{},justifyContent:{},alignItems:{},alignContent:{},order:{},flex:{},flexGrow:{},flexShrink:{},alignSelf:{},justifyItems:{},justifySelf:{},gap:{style:sc},rowGap:{style:ac},columnGap:{style:ic},gridColumn:{},gridRow:{},gridAutoFlow:{},gridAutoColumns:{},gridAutoRows:{},gridTemplateColumns:{},gridTemplateRows:{},gridTemplateAreas:{},gridArea:{},position:{},zIndex:{themeKey:"zIndex"},top:{},right:{},bottom:{},left:{},boxShadow:{themeKey:"shadows"},width:{transform:Lr},maxWidth:{style:nf},minWidth:{transform:Lr},height:{transform:Lr},maxHeight:{transform:Lr},minHeight:{transform:Lr},boxSizing:{},fontFamily:{themeKey:"typography"},fontSize:{themeKey:"typography"},fontStyle:{themeKey:"typography"},fontWeight:{themeKey:"typography"},letterSpacing:{},textTransform:{},lineHeight:{},textAlign:{},typography:{cssProperty:!1,themeKey:"typography"}},Xa=Kj;function Gj(...e){let t=e.reduce((o,n)=>o.concat(Object.keys(n)),[]),r=new Set(t);return e.every(o=>r.size===Object.keys(o).length)}function Yj(e,t){return typeof e=="function"?e(t):e}function Xj(){function e(r,o,n,s){let i={[r]:o,theme:n},a=s[r];if(!a)return{[r]:o};let{cssProperty:l=r,themeKey:p,transform:c,style:u}=a;if(o==null)return null;if(p==="typography"&&o==="inherit")return{[r]:o};let f=Ya(n,p)||{};return u?u(i):Vt(i,o,x=>{let h=rc(f,c,x);return x===h&&typeof x=="string"&&(h=rc(f,c,`${r}${x==="default"?"":(0,D$.default)(x)}`,x)),l===!1?h:{[l]:h}})}function t(r){var o;let{sx:n,theme:s={},nested:i}=r||{};if(!n)return null;let a=(o=s.unstable_sxConfig)!=null?o:Xa;function l(p){let c=p;if(typeof p=="function")c=p(s);else if(typeof p!="object")return p;if(!c)return null;let u=cv(s.breakpoints),f=Object.keys(u),v=u;return Object.keys(c).forEach(x=>{let h=Yj(c[x],s);if(h!=null)if(typeof h=="object")if(a[x])v=bs(v,e(x,h,s,a));else{let b=Vt({theme:s},h,y=>({[x]:y}));Gj(b,h)?v[x]=t({sx:h,theme:s,nested:!0}):v=bs(v,b)}else v=bs(v,e(x,h,s,a))}),!i&&s.modularCssLayers?{"@layer sx":rf(f,v)}:rf(f,v)}return Array.isArray(n)?n.map(l):l(n)}return t}var L$=Xj();L$.filterProps=["sx"];var mi=L$;function vv(e,t){let r=this;return r.vars&&typeof r.getColorSchemeSelector=="function"?{[r.getColorSchemeSelector(e).replace(/(\[[^\]]+\])/,"*:where($1)")]:t}:r.palette.mode===e?t:{}}var Qj=["breakpoints","palette","spacing","shape"];function Zj(e={},...t){let{breakpoints:r={},palette:o={},spacing:n,shape:s={}}=e,i=k(e,Qj),a=pv(r),l=gv(n),p=(0,xv.default)({breakpoints:a,direction:"ltr",components:{},palette:d({mode:"light"},o),spacing:l,shape:d({},_$,s)},i);return p.applyStyles=vv,p=t.reduce((c,u)=>(0,xv.default)(c,u),p),p.unstable_sxConfig=d({},Xa,i?.unstable_sxConfig),p.unstable_sx=function(u){return mi({sx:u,theme:this})},p}var yi=Zj;var A$=P(L()),z$=P(On());function Jj(e){return Object.keys(e).length===0}function eD(e=null){let t=A$.useContext(z$.ThemeContext);return!t||Jj(t)?e:t}var Cs=eD;var tD=yi();function rD(e=tD){return Cs(e)}var Mn=rD;var B$=P(H());function Tv(e){let t=(0,sf.internal_serializeStyles)(e);return e!==t&&t.styles?(t.styles.match(/^@layer\s+[^{]*$/)||(t.styles=`@layer global{${t.styles}}`),t):e}function oD({styles:e,themeId:t,defaultTheme:r={}}){let o=Mn(r),n=t&&o[t]||o,s=typeof e=="function"?e(n):e;return n.modularCssLayers&&(Array.isArray(s)?s=s.map(i=>Tv(typeof i=="function"?i(n):i)):s=Tv(s)),(0,B$.jsx)(sf.GlobalStyles,{styles:s})}var Qa=oD;J();var F$=P(Wt());var nD=["sx"],sD=e=>{var t,r;let o={systemProps:{},otherProps:{}},n=(t=e==null||(r=e.theme)==null?void 0:r.unstable_sxConfig)!=null?t:Xa;return Object.keys(e).forEach(s=>{n[s]?o.systemProps[s]=e[s]:o.otherProps[s]=e[s]}),o};function Za(e){let{sx:t}=e,r=k(e,nD),{systemProps:o,otherProps:n}=sD(r),s;return Array.isArray(t)?s=[o,...t]:typeof t=="function"?s=(...i)=>{let a=t(...i);return(0,F$.isPlainObject)(a)?d({},o,a):o}:s=d({},o,t),d({},n,{sx:s})}var U$=e=>e,iD=()=>{let e=U$;return{configure(t){e=t},generate(t){return e(t)},reset(){e=U$}}},aD=iD(),hi=aD;J();var V$=P(L());function W$(e){var t,r,o="";if(typeof e=="string"||typeof e=="number")o+=e;else if(typeof e=="object")if(Array.isArray(e)){var n=e.length;for(t=0;t<n;t++)e[t]&&(r=W$(e[t]))&&(o&&(o+=" "),o+=r)}else for(r in e)e[r]&&(o&&(o+=" "),o+=r);return o}function lD(){for(var e,t,r=0,o="",n=arguments.length;r<n;r++)(e=arguments[r])&&(t=W$(e))&&(o&&(o+=" "),o+=t);return o}var A=lD;var H$=P(On());var q$=P(H()),pD=["className","component"];function af(e={}){let{themeId:t,defaultTheme:r,defaultClassName:o="MuiBox-root",generateClassName:n}=e,s=(0,H$.default)("div",{shouldForwardProp:a=>a!=="theme"&&a!=="sx"&&a!=="as"})(mi);return V$.forwardRef(function(l,p){let c=Mn(r),u=Za(l),{className:f,component:v="div"}=u,x=k(u,pD);return(0,q$.jsx)(s,d({as:v,ref:p,className:A(f,n?n(o):o),theme:t&&c[t]||c},x))})}var cD={active:"active",checked:"checked",completed:"completed",disabled:"disabled",error:"error",expanded:"expanded",focused:"focused",focusVisible:"focusVisible",open:"open",readOnly:"readOnly",required:"required",selected:"selected"};function K(e,t,r="Mui"){let o=cD[t];return o?`${r}-${o}`:`${hi.generate(e)}-${t}`}function W(e,t,r="Mui"){let o={};return t.forEach(n=>{o[n]=K(e,n,r)}),o}J();var gi=P(On()),nw=P(Wt());var gD=["ownerState"],vD=["variants"],xD=["name","slot","skipVariantsResolver","skipSx","overridesResolver"];function TD(e){return Object.keys(e).length===0}function bD(e){return typeof e=="string"&&e.charCodeAt(0)>96}function Cv(e){return e!=="ownerState"&&e!=="theme"&&e!=="sx"&&e!=="as"}function ow(e,t){return t&&e&&typeof e=="object"&&e.styles&&!e.styles.startsWith("@layer")&&(e.styles=`@layer ${t}{${String(e.styles)}}`),e}var PD=yi(),CD=e=>e&&e.charAt(0).toLowerCase()+e.slice(1);function Tf({defaultTheme:e,theme:t,themeId:r}){return TD(t)?e:t[r]||t}function $D(e){return e?(t,r)=>r[e]:null}function bf(e,t,r){let{ownerState:o}=t,n=k(t,gD),s=typeof e=="function"?e(d({ownerState:o},n)):e;if(Array.isArray(s))return s.flatMap(i=>bf(i,d({ownerState:o},n),r));if(s&&typeof s=="object"&&Array.isArray(s.variants)){let{variants:i=[]}=s,l=k(s,vD);return i.forEach(p=>{let c=!0;if(typeof p.props=="function"?c=p.props(d({ownerState:o},n,o)):Object.keys(p.props).forEach(u=>{o?.[u]!==p.props[u]&&n[u]!==p.props[u]&&(c=!1)}),c){Array.isArray(l)||(l=[l]);let u=typeof p.style=="function"?p.style(d({ownerState:o},n,o)):p.style;l.push(r?ow((0,gi.internal_serializeStyles)(u),r):u)}}),l}return r?ow((0,gi.internal_serializeStyles)(s),r):s}function $v(e={}){let{themeId:t,defaultTheme:r=PD,rootShouldForwardProp:o=Cv,slotShouldForwardProp:n=Cv}=e,s=i=>mi(d({},i,{theme:Tf(d({},i,{defaultTheme:r,themeId:t}))}));return s.__mui_systemSx=!0,(i,a={})=>{(0,gi.internal_processStyles)(i,$=>$.filter(C=>!(C!=null&&C.__mui_systemSx)));let{name:l,slot:p,skipVariantsResolver:c,skipSx:u,overridesResolver:f=$D(CD(p))}=a,v=k(a,xD),x=l&&l.startsWith("Mui")||p?"components":"custom",h=c!==void 0?c:p&&p!=="Root"&&p!=="root"||!1,b=u||!1,y,m=Cv;p==="Root"||p==="root"?m=o:p?m=n:bD(i)&&(m=void 0);let g=(0,gi.default)(i,d({shouldForwardProp:m,label:y},v)),T=$=>typeof $=="function"&&$.__emotion_real!==$||(0,nw.isPlainObject)($)?C=>{let _=Tf({theme:C.theme,defaultTheme:r,themeId:t});return bf($,d({},C,{theme:_}),_.modularCssLayers?x:void 0)}:$,w=($,...C)=>{let _=T($),S=C?C.map(T):[];l&&f&&S.push(U=>{let z=Tf(d({},U,{defaultTheme:r,themeId:t}));if(!z.components||!z.components[l]||!z.components[l].styleOverrides)return null;let Z=z.components[l].styleOverrides,B={};return Object.entries(Z).forEach(([D,q])=>{B[D]=bf(q,d({},U,{theme:z}),z.modularCssLayers?"theme":void 0)}),f(U,B)}),l&&!h&&S.push(U=>{var z;let Z=Tf(d({},U,{defaultTheme:r,themeId:t})),B=Z==null||(z=Z.components)==null||(z=z[l])==null?void 0:z.variants;return bf({variants:B},d({},U,{theme:Z}),Z.modularCssLayers?"theme":void 0)}),b||S.push(s);let R=S.length-C.length;if(Array.isArray($)&&R>0){let U=new Array(R).fill("");_=[...$,...U],_.raw=[...$.raw,...U]}let j=g(_,...S);return i.muiName&&(j.muiName=i.muiName),j};return g.withConfig&&(w.withConfig=g.withConfig),w}}var wD=$v(),sw=wD;J();function dn(e,t){let r=d({},t);return Object.keys(e).forEach(o=>{if(o.toString().match(/^(components|slots)$/))r[o]=d({},e[o],r[o]);else if(o.toString().match(/^(componentsProps|slotProps)$/)){let n=e[o]||{},s=t[o];r[o]={},!s||!Object.keys(s)?r[o]=n:!n||!Object.keys(n)?r[o]=s:(r[o]=d({},s),Object.keys(n).forEach(i=>{r[o][i]=dn(n[i],s[i])}))}else r[o]===void 0&&(r[o]=e[o])}),r}function el(e){let{theme:t,name:r,props:o}=e;return!t||!t.components||!t.components[r]||!t.components[r].defaultProps?o:dn(t.components[r].defaultProps,o)}function Pf({props:e,name:t,defaultTheme:r,themeId:o}){let n=Mn(r);return o&&(n=n[o]||n),el({theme:n,name:t,props:e})}var fn=P(L());var Cf=P(L()),_D=typeof window<"u"?Cf.useLayoutEffect:Cf.useEffect,Nt=_D;function RD(e,t,r,o,n){let[s,i]=fn.useState(()=>n&&r?r(e).matches:o?o(e).matches:t);return Nt(()=>{let a=!0;if(!r)return;let l=r(e),p=()=>{a&&i(l.matches)};return p(),l.addListener(p),()=>{a=!1,l.removeListener(p)}},[e,r]),s}var iw=fn.useSyncExternalStore;function ED(e,t,r,o,n){let s=fn.useCallback(()=>t,[t]),i=fn.useMemo(()=>{if(n&&r)return()=>r(e).matches;if(o!==null){let{matches:c}=o(e);return()=>c}return s},[s,e,o,n,r]),[a,l]=fn.useMemo(()=>{if(r===null)return[s,()=>()=>{}];let c=r(e);return[()=>c.matches,u=>(c.addListener(u),()=>{c.removeListener(u)})]},[s,r,e]);return iw(l,a,i)}function In(e,t={}){let r=Cs(),o=typeof window<"u"&&typeof window.matchMedia<"u",{defaultMatches:n=!1,matchMedia:s=o?window.matchMedia:null,ssrMatchMedia:i=null,noSsr:a=!1}=el({name:"MuiUseMediaQuery",props:t,theme:r}),l=typeof e=="function"?e(r):e;return l=l.replace(/^@media( ?)/m,""),(iw!==void 0?ED:RD)(l,n,s,i,a)}J();var Sw=P(L());J();var xw=P(L());function tl(...e){return e.reduce((t,r)=>r==null?t:function(...n){t.apply(this,n),r.apply(this,n)},()=>{})}function vi(e,t=166){let r;function o(...n){let s=()=>{e.apply(this,n)};clearTimeout(r),r=setTimeout(s,t)}return o.clear=()=>{clearTimeout(r)},o}var pw=P(L());function wf(e,t){var r,o;return pw.isValidElement(e)&&t.indexOf((r=e.type.muiName)!=null?r:(o=e.type)==null||(o=o._payload)==null||(o=o.value)==null?void 0:o.muiName)!==-1}function rt(e){return e&&e.ownerDocument||document}function xo(e){return rt(e).defaultView||window}function $s(e,t){typeof e=="function"?e(t):e&&(e.current=t)}var rl=P(L()),cw=0;function ND(e){let[t,r]=rl.useState(e),o=e||t;return rl.useEffect(()=>{t==null&&(cw+=1,r(`mui-${cw}`))},[t]),o}var uw=rl.useId;function To(e){if(uw!==void 0){let t=uw();return e??t}return ND(e)}var xi=P(L());function _f({controlled:e,default:t,name:r,state:o="value"}){let{current:n}=xi.useRef(e!==void 0),[s,i]=xi.useState(t),a=n?e:s,l=xi.useCallback(p=>{n||i(p)},[]);return[a,l]}var _v=P(L());function MD(e){let t=_v.useRef(e);return Nt(()=>{t.current=e}),_v.useRef((...r)=>(0,t.current)(...r)).current}var bo=MD;var dw=P(L());function yt(...e){return dw.useMemo(()=>e.every(t=>t==null)?null:t=>{e.forEach(r=>{$s(r,t)})},e)}var mw=P(L()),fw={};function Rv(e,t){let r=mw.useRef(fw);return r.current===fw&&(r.current=e(t)),r}var yw=P(L()),ID=[];function Ev(e){yw.useEffect(e,ID)}var jn=class e{constructor(){this.currentId=null,this.clear=()=>{this.currentId!==null&&(clearTimeout(this.currentId),this.currentId=null)},this.disposeEffect=()=>this.clear}static create(){return new e}start(t,r){this.clear(),this.currentId=setTimeout(()=>{this.currentId=null,r()},t)}};function Ar(){let e=Rv(jn.create).current;return Ev(e.disposeEffect),e}var Rf=P(L());var Ef=!0,kv=!1,jD=new jn,DD={text:!0,search:!0,url:!0,tel:!0,email:!0,password:!0,number:!0,date:!0,month:!0,week:!0,time:!0,datetime:!0,"datetime-local":!0};function LD(e){let{type:t,tagName:r}=e;return!!(r==="INPUT"&&DD[t]&&!e.readOnly||r==="TEXTAREA"&&!e.readOnly||e.isContentEditable)}function AD(e){e.metaKey||e.altKey||e.ctrlKey||(Ef=!0)}function Sv(){Ef=!1}function zD(){this.visibilityState==="hidden"&&kv&&(Ef=!0)}function BD(e){e.addEventListener("keydown",AD,!0),e.addEventListener("mousedown",Sv,!0),e.addEventListener("pointerdown",Sv,!0),e.addEventListener("touchstart",Sv,!0),e.addEventListener("visibilitychange",zD,!0)}function FD(e){let{target:t}=e;try{return t.matches(":focus-visible")}catch{}return Ef||LD(t)}function Sf(){let e=Rf.useCallback(n=>{n!=null&&BD(n.ownerDocument)},[]),t=Rf.useRef(!1);function r(){return t.current?(kv=!0,jD.start(100,()=>{kv=!1}),t.current=!1,!0):!1}function o(n){return FD(n)?(t.current=!0,!0):!1}return{isFocusVisibleRef:t,onFocus:o,onBlur:r,ref:e}}function Ti(e){let t=e.documentElement.clientWidth;return Math.abs(window.innerWidth-t)}function G(e,t,r=void 0){let o={};return Object.keys(e).forEach(n=>{o[n]=e[n].reduce((s,i)=>{if(i){let a=t(i);a!==""&&s.push(a),r&&r[i]&&s.push(r[i])}return s},[]).join(" ")}),o}J();J();function UD(e){return typeof e=="string"}var ws=UD;function WD(e,t,r){return e===void 0||ws(e)?t:d({},t,{ownerState:d({},t.ownerState,r)})}var mn=WD;J();function VD(e,t=[]){if(e===void 0)return{};let r={};return Object.keys(e).filter(o=>o.match(/^on[A-Z]/)&&typeof e[o]=="function"&&!t.includes(o)).forEach(o=>{r[o]=e[o]}),r}var _s=VD;function HD(e){if(e===void 0)return{};let t={};return Object.keys(e).filter(r=>!(r.match(/^on[A-Z]/)&&typeof e[r]=="function")).forEach(r=>{t[r]=e[r]}),t}var kf=HD;function qD(e){let{getSlotProps:t,additionalProps:r,externalSlotProps:o,externalForwardedProps:n,className:s}=e;if(!t){let v=A(r?.className,s,n?.className,o?.className),x=d({},r?.style,n?.style,o?.style),h=d({},r,n,o);return v.length>0&&(h.className=v),Object.keys(x).length>0&&(h.style=x),{props:h,internalRef:void 0}}let i=_s(d({},n,o)),a=kf(o),l=kf(n),p=t(i),c=A(p?.className,r?.className,s,n?.className,o?.className),u=d({},p?.style,r?.style,n?.style,o?.style),f=d({},p,r,l,a);return c.length>0&&(f.className=c),Object.keys(u).length>0&&(f.style=u),{props:f,internalRef:p.ref}}var lc=qD;function KD(e,t,r){return typeof e=="function"?e(t,r):e}var pc=KD;var GD=["elementType","externalSlotProps","ownerState","skipResolvingSlotProps"];function YD(e){var t;let{elementType:r,externalSlotProps:o,ownerState:n,skipResolvingSlotProps:s=!1}=e,i=k(e,GD),a=s?{}:pc(o,n),{props:l,internalRef:p}=lc(d({},i,{externalSlotProps:a})),c=yt(p,a?.ref,(t=e.additionalProps)==null?void 0:t.ref);return mn(r,d({},l,{ref:c}),n)}var zr=YD;var hw=P(L());function Mt(e){if(parseInt(hw.version,10)>=19){var t;return(e==null||(t=e.props)==null?void 0:t.ref)||null}return e?.ref||null}var gw=P(L()),XD=gw.createContext(null),Of=XD;var Ov=P(L());function bi(){return Ov.useContext(Of)}var QD=typeof Symbol=="function"&&Symbol.for,vw=QD?Symbol.for("mui.nested"):"__THEME_NESTED__";var Tw=P(H());function ZD(e,t){return typeof t=="function"?t(e):d({},e,t)}function JD(e){let{children:t,theme:r}=e,o=bi(),n=xw.useMemo(()=>{let s=o===null?r:ZD(o,r);return s!=null&&(s[vw]=o!==null),s},[r,o]);return(0,Tw.jsx)(Of.Provider,{value:n,children:t})}var Nf=JD;var kw=P(On());J();var Mf=P(L());var bw=P(H()),eL=["value"],Pw=Mf.createContext();function tL(e){let{value:t}=e,r=k(e,eL);return(0,bw.jsx)(Pw.Provider,d({value:t??!0},r))}var Rs=()=>{let e=Mf.useContext(Pw);return e??!1},Cw=tL;var If=P(L());var $w=P(H()),ww=If.createContext(void 0);function rL({value:e,children:t}){return(0,$w.jsx)(ww.Provider,{value:e,children:t})}function oL(e){let{theme:t,name:r,props:o}=e;if(!t||!t.components||!t.components[r])return o;let n=t.components[r];return n.defaultProps?dn(n.defaultProps,o):!n.styleOverrides&&!n.variants?dn(n,o):o}function Nv({props:e,name:t}){let r=If.useContext(ww);return oL({props:e,name:t,theme:{components:r}})}var jf=rL;var OK=P(L());var _w=P(H());function Mv(e){let t=Cs(),r=To()||"",{modularCssLayers:o}=e,n="mui.global, mui.components, mui.theme, mui.custom, mui.sx";return!o||t!==null?n="":typeof o=="string"?n=o.replace(/mui(?!\.)/g,n):n=`@layer ${n};`,Nt(()=>{let s=document.querySelector("head");if(!s)return;let i=s.firstChild;if(n){var a;if(i&&(a=i.hasAttribute)!=null&&a.call(i,"data-mui-layer-order")&&i.getAttribute("data-mui-layer-order")===r)return;let p=document.createElement("style");p.setAttribute("data-mui-layer-order",r),p.textContent=n,s.prepend(p)}else{var l;(l=s.querySelector(`style[data-mui-layer-order="${r}"]`))==null||l.remove()}},[n,r]),n?(0,_w.jsx)(Qa,{styles:n}):null}var Ow=P(H()),Df=P(H()),Rw={};function Ew(e,t,r,o=!1){return Sw.useMemo(()=>{let n=e&&t[e]||t;if(typeof r=="function"){let s=r(n),i=e?d({},t,{[e]:s}):s;return o?()=>i:i}return e?d({},t,{[e]:r}):d({},t,r)},[e,t,r,o])}function nL(e){let{children:t,theme:r,themeId:o}=e,n=Cs(Rw),s=bi()||Rw,i=Ew(o,n,r),a=Ew(o,s,r,!0),l=i.direction==="rtl",p=Mv(i);return(0,Df.jsx)(Nf,{theme:a,children:(0,Df.jsx)(kw.ThemeContext.Provider,{value:i,children:(0,Df.jsx)(Cw,{value:l,children:(0,Ow.jsxs)(jf,{value:i?.components,children:[p,t]})})})})}var Lf=nL;J();var ol=P(L());var Nw=P(Wt());var Mw=P(H()),sL=["component","direction","spacing","divider","children","className","useFlexGap"],iL=yi(),aL=sw("div",{name:"MuiStack",slot:"Root",overridesResolver:(e,t)=>t.root});function lL(e){return Pf({props:e,name:"MuiStack",defaultTheme:iL})}function pL(e,t){let r=ol.Children.toArray(e).filter(Boolean);return r.reduce((o,n,s)=>(o.push(n),s<r.length-1&&o.push(ol.cloneElement(t,{key:`separator-${s}`})),o),[])}var cL=e=>({row:"Left","row-reverse":"Right",column:"Top","column-reverse":"Bottom"})[e],uL=({ownerState:e,theme:t})=>{let r=d({display:"flex",flexDirection:"column"},Vt({theme:t},of({values:e.direction,breakpoints:t.breakpoints.values}),o=>({flexDirection:o})));if(e.spacing){let o=oc(t),n=Object.keys(t.breakpoints.values).reduce((l,p)=>((typeof e.spacing=="object"&&e.spacing[p]!=null||typeof e.direction=="object"&&e.direction[p]!=null)&&(l[p]=!0),l),{}),s=of({values:e.direction,base:n}),i=of({values:e.spacing,base:n});typeof s=="object"&&Object.keys(s).forEach((l,p,c)=>{if(!s[l]){let f=p>0?s[c[p-1]]:"column";s[l]=f}}),r=(0,Nw.default)(r,Vt({theme:t},i,(l,p)=>e.useFlexGap?{gap:un(o,l)}:{"& > :not(style):not(style)":{margin:0},"& > :not(style) ~ :not(style)":{[`margin${cL(p?s[p]:e.direction)}`]:un(o,l)}}))}return r=k$(t.breakpoints,r),r};function Af(e={}){let{createStyledComponent:t=aL,useThemeProps:r=lL,componentName:o="MuiStack"}=e,n=()=>G({root:["root"]},l=>K(o,l),{}),s=t(uL);return ol.forwardRef(function(l,p){let c=r(l),u=Za(c),{component:f="div",direction:v="column",spacing:x=0,divider:h,children:b,className:y,useFlexGap:m=!1}=u,g=k(u,sL),T={direction:v,spacing:x,useFlexGap:m},w=n();return(0,Mw.jsx)(s,d({as:f,ownerState:T,ref:p,className:A(w.root,y)},g,{children:h?pL(b,h):b}))})}var Ho="$$material";var Iw=P(H()),dL=["theme"];function nl(e){let{theme:t}=e,r=k(e,dL),o=t[Ho];return(0,Iw.jsx)(Lf,d({},r,{themeId:o?Ho:void 0,theme:o||t}))}J();var k_=P(ni()),Jf=P(Wt()),em=P(Yf()),O_=P(ux());J();function dx(e,t){return d({toolbar:{minHeight:56,[e.up("xs")]:{"@media (orientation: landscape)":{minHeight:48}},[e.up("sm")]:{minHeight:64}}},t)}J();var gx=P(ni()),C_=P(Wt()),dl=P($r());var g4={black:"#000",white:"#fff"},cl=g4;var v4={50:"#fafafa",100:"#f5f5f5",200:"#eeeeee",300:"#e0e0e0",400:"#bdbdbd",500:"#9e9e9e",600:"#757575",700:"#616161",800:"#424242",900:"#212121",A100:"#f5f5f5",A200:"#eeeeee",A400:"#bdbdbd",A700:"#616161"},T_=v4;var x4={50:"#f3e5f5",100:"#e1bee7",200:"#ce93d8",300:"#ba68c8",400:"#ab47bc",500:"#9c27b0",600:"#8e24aa",700:"#7b1fa2",800:"#6a1b9a",900:"#4a148c",A100:"#ea80fc",A200:"#e040fb",A400:"#d500f9",A700:"#aa00ff"},_i=x4;var T4={50:"#ffebee",100:"#ffcdd2",200:"#ef9a9a",300:"#e57373",400:"#ef5350",500:"#f44336",600:"#e53935",700:"#d32f2f",800:"#c62828",900:"#b71c1c",A100:"#ff8a80",A200:"#ff5252",A400:"#ff1744",A700:"#d50000"},Ri=T4;var b4={50:"#fff3e0",100:"#ffe0b2",200:"#ffcc80",300:"#ffb74d",400:"#ffa726",500:"#ff9800",600:"#fb8c00",700:"#f57c00",800:"#ef6c00",900:"#e65100",A100:"#ffd180",A200:"#ffab40",A400:"#ff9100",A700:"#ff6d00"},ul=b4;var P4={50:"#e3f2fd",100:"#bbdefb",200:"#90caf9",300:"#64b5f6",400:"#42a5f5",500:"#2196f3",600:"#1e88e5",700:"#1976d2",800:"#1565c0",900:"#0d47a1",A100:"#82b1ff",A200:"#448aff",A400:"#2979ff",A700:"#2962ff"},Ei=P4;var C4={50:"#e1f5fe",100:"#b3e5fc",200:"#81d4fa",300:"#4fc3f7",400:"#29b6f6",500:"#03a9f4",600:"#039be5",700:"#0288d1",800:"#0277bd",900:"#01579b",A100:"#80d8ff",A200:"#40c4ff",A400:"#00b0ff",A700:"#0091ea"},Si=C4;var $4={50:"#e8f5e9",100:"#c8e6c9",200:"#a5d6a7",300:"#81c784",400:"#66bb6a",500:"#4caf50",600:"#43a047",700:"#388e3c",800:"#2e7d32",900:"#1b5e20",A100:"#b9f6ca",A200:"#69f0ae",A400:"#00e676",A700:"#00c853"},ki=$4;var w4=["mode","contrastThreshold","tonalOffset"],b_={text:{primary:"rgba(0, 0, 0, 0.87)",secondary:"rgba(0, 0, 0, 0.6)",disabled:"rgba(0, 0, 0, 0.38)"},divider:"rgba(0, 0, 0, 0.12)",background:{paper:cl.white,default:cl.white},action:{active:"rgba(0, 0, 0, 0.54)",hover:"rgba(0, 0, 0, 0.04)",hoverOpacity:.04,selected:"rgba(0, 0, 0, 0.08)",selectedOpacity:.08,disabled:"rgba(0, 0, 0, 0.26)",disabledBackground:"rgba(0, 0, 0, 0.12)",disabledOpacity:.38,focus:"rgba(0, 0, 0, 0.12)",focusOpacity:.12,activatedOpacity:.12}},hx={text:{primary:cl.white,secondary:"rgba(255, 255, 255, 0.7)",disabled:"rgba(255, 255, 255, 0.5)",icon:"rgba(255, 255, 255, 0.5)"},divider:"rgba(255, 255, 255, 0.12)",background:{paper:"#121212",default:"#121212"},action:{active:cl.white,hover:"rgba(255, 255, 255, 0.08)",hoverOpacity:.08,selected:"rgba(255, 255, 255, 0.16)",selectedOpacity:.16,disabled:"rgba(255, 255, 255, 0.3)",disabledBackground:"rgba(255, 255, 255, 0.12)",disabledOpacity:.38,focus:"rgba(255, 255, 255, 0.12)",focusOpacity:.12,activatedOpacity:.24}};function P_(e,t,r,o){let n=o.light||o,s=o.dark||o*1.5;e[t]||(e.hasOwnProperty(r)?e[t]=e[r]:t==="light"?e.light=(0,dl.lighten)(e.main,n):t==="dark"&&(e.dark=(0,dl.darken)(e.main,s)))}function _4(e="light"){return e==="dark"?{main:Ei[200],light:Ei[50],dark:Ei[400]}:{main:Ei[700],light:Ei[400],dark:Ei[800]}}function R4(e="light"){return e==="dark"?{main:_i[200],light:_i[50],dark:_i[400]}:{main:_i[500],light:_i[300],dark:_i[700]}}function E4(e="light"){return e==="dark"?{main:Ri[500],light:Ri[300],dark:Ri[700]}:{main:Ri[700],light:Ri[400],dark:Ri[800]}}function S4(e="light"){return e==="dark"?{main:Si[400],light:Si[300],dark:Si[700]}:{main:Si[700],light:Si[500],dark:Si[900]}}function k4(e="light"){return e==="dark"?{main:ki[400],light:ki[300],dark:ki[700]}:{main:ki[800],light:ki[500],dark:ki[900]}}function O4(e="light"){return e==="dark"?{main:ul[400],light:ul[300],dark:ul[700]}:{main:"#ed6c02",light:ul[500],dark:ul[900]}}function vx(e){let{mode:t="light",contrastThreshold:r=3,tonalOffset:o=.2}=e,n=k(e,w4),s=e.primary||_4(t),i=e.secondary||R4(t),a=e.error||E4(t),l=e.info||S4(t),p=e.success||k4(t),c=e.warning||O4(t);function u(h){return(0,dl.getContrastRatio)(h,hx.text.primary)>=r?hx.text.primary:b_.text.primary}let f=({color:h,name:b,mainShade:y=500,lightShade:m=300,darkShade:g=700})=>{if(h=d({},h),!h.main&&h[y]&&(h.main=h[y]),!h.hasOwnProperty("main"))throw new Error((0,gx.default)(11,b?` (${b})`:"",y));if(typeof h.main!="string")throw new Error((0,gx.default)(12,b?` (${b})`:"",JSON.stringify(h.main)));return P_(h,"light",m,o),P_(h,"dark",g,o),h.contrastText||(h.contrastText=u(h.main)),h},v={dark:hx,light:b_};return(0,C_.default)(d({common:d({},cl),mode:t,primary:f({color:s,name:"primary"}),secondary:f({color:i,name:"secondary",mainShade:"A400",lightShade:"A200",darkShade:"A700"}),error:f({color:a,name:"error"}),warning:f({color:c,name:"warning"}),info:f({color:l,name:"info"}),success:f({color:p,name:"success"}),grey:T_,contrastThreshold:r,getContrastText:u,augmentColor:f,tonalOffset:o},v[t]),n)}J();var __=P(Wt()),N4=["fontFamily","fontSize","fontWeightLight","fontWeightRegular","fontWeightMedium","fontWeightBold","htmlFontSize","allVariants","pxToRem"];function M4(e){return Math.round(e*1e5)/1e5}var $_={textTransform:"uppercase"},w_='"Roboto", "Helvetica", "Arial", sans-serif';function xx(e,t){let r=typeof t=="function"?t(e):t,{fontFamily:o=w_,fontSize:n=14,fontWeightLight:s=300,fontWeightRegular:i=400,fontWeightMedium:a=500,fontWeightBold:l=700,htmlFontSize:p=16,allVariants:c,pxToRem:u}=r,f=k(r,N4),v=n/14,x=u||(y=>`${y/p*v}rem`),h=(y,m,g,T,w)=>d({fontFamily:o,fontWeight:y,fontSize:x(m),lineHeight:g},o===w_?{letterSpacing:`${M4(T/m)}em`}:{},w,c),b={h1:h(s,96,1.167,-1.5),h2:h(s,60,1.2,-.5),h3:h(i,48,1.167,0),h4:h(i,34,1.235,.25),h5:h(i,24,1.334,0),h6:h(a,20,1.6,.15),subtitle1:h(i,16,1.75,.15),subtitle2:h(a,14,1.57,.1),body1:h(i,16,1.5,.15),body2:h(i,14,1.43,.15),button:h(a,14,1.75,.4,$_),caption:h(i,12,1.66,.4),overline:h(i,12,2.66,1,$_),inherit:{fontFamily:"inherit",fontWeight:"inherit",fontSize:"inherit",lineHeight:"inherit",letterSpacing:"inherit"}};return(0,__.default)(d({htmlFontSize:p,pxToRem:x,fontFamily:o,fontSize:n,fontWeightLight:s,fontWeightRegular:i,fontWeightMedium:a,fontWeightBold:l},b),f,{clone:!1})}function ot(...e){return[`${e[0]}px ${e[1]}px ${e[2]}px ${e[3]}px rgba(0,0,0,${.2})`,`${e[4]}px ${e[5]}px ${e[6]}px ${e[7]}px rgba(0,0,0,${.14})`,`${e[8]}px ${e[9]}px ${e[10]}px ${e[11]}px rgba(0,0,0,${.12})`].join(",")}var I4=["none",ot(0,2,1,-1,0,1,1,0,0,1,3,0),ot(0,3,1,-2,0,2,2,0,0,1,5,0),ot(0,3,3,-2,0,3,4,0,0,1,8,0),ot(0,2,4,-1,0,4,5,0,0,1,10,0),ot(0,3,5,-1,0,5,8,0,0,1,14,0),ot(0,3,5,-1,0,6,10,0,0,1,18,0),ot(0,4,5,-2,0,7,10,1,0,2,16,1),ot(0,5,5,-3,0,8,10,1,0,3,14,2),ot(0,5,6,-3,0,9,12,1,0,3,16,2),ot(0,6,6,-3,0,10,14,1,0,4,18,3),ot(0,6,7,-4,0,11,15,1,0,4,20,3),ot(0,7,8,-4,0,12,17,2,0,5,22,4),ot(0,7,8,-4,0,13,19,2,0,5,24,4),ot(0,7,9,-4,0,14,21,2,0,5,26,4),ot(0,8,9,-5,0,15,22,2,0,6,28,5),ot(0,8,10,-5,0,16,24,2,0,6,30,5),ot(0,8,11,-5,0,17,26,2,0,6,32,5),ot(0,9,11,-5,0,18,28,2,0,7,34,6),ot(0,9,12,-6,0,19,29,2,0,7,36,6),ot(0,10,13,-6,0,20,31,3,0,8,38,7),ot(0,10,13,-6,0,21,33,3,0,8,40,7),ot(0,10,14,-6,0,22,35,3,0,8,42,7),ot(0,11,14,-7,0,23,36,3,0,9,44,8),ot(0,11,15,-7,0,24,38,3,0,9,46,8)],R_=I4;J();var j4=["duration","easing","delay"],D4={easeInOut:"cubic-bezier(0.4, 0, 0.2, 1)",easeOut:"cubic-bezier(0.0, 0, 0.2, 1)",easeIn:"cubic-bezier(0.4, 0, 1, 1)",sharp:"cubic-bezier(0.4, 0, 0.6, 1)"},L4={shortest:150,shorter:200,short:250,standard:300,complex:375,enteringScreen:225,leavingScreen:195};function E_(e){return`${Math.round(e)}ms`}function A4(e){if(!e)return 0;let t=e/36;return Math.round((4+15*t**.25+t/5)*10)}function Tx(e){let t=d({},D4,e.easing),r=d({},L4,e.duration);return d({getAutoHeightDuration:A4,create:(n=["all"],s={})=>{let{duration:i=r.standard,easing:a=t.easeInOut,delay:l=0}=s,p=k(s,j4);return(Array.isArray(n)?n:[n]).map(c=>`${c} ${typeof i=="string"?i:E_(i)} ${a} ${typeof l=="string"?l:E_(l)}`).join(",")}},e,{easing:t,duration:r})}var z4={mobileStepper:1e3,fab:1050,speedDial:1050,appBar:1100,drawer:1200,modal:1300,snackbar:1400,tooltip:1500},S_=z4;var B4=["breakpoints","mixins","spacing","palette","transitions","typography","shape"];function F4(e={},...t){let{mixins:r={},palette:o={},transitions:n={},typography:s={}}=e,i=k(e,B4);if(e.vars)throw new Error((0,k_.default)(18));let a=vx(o),l=(0,O_.default)(e),p=(0,Jf.default)(l,{mixins:dx(l.breakpoints,r),palette:a,shadows:R_.slice(),typography:xx(a,s),transitions:Tx(n),zIndex:d({},S_)});return p=(0,Jf.default)(p,i),p=t.reduce((c,u)=>(0,Jf.default)(c,u),p),p.unstable_sxConfig=d({},em.unstable_defaultSxConfig,i?.unstable_sxConfig),p.unstable_sx=function(u){return(0,em.default)({sx:u,theme:this})},p}var Ss=F4;J();var PR=P(L());var xl=P($r());var U4=Ss(),fl=U4;var j_=P(I_());function rA(e){return e!=="ownerState"&&e!=="theme"&&e!=="sx"&&e!=="as"}var bc=rA;var oA=e=>bc(e)&&e!=="classes",je=oA;var nA=(0,j_.default)({themeId:Ho,defaultTheme:fl,rootShouldForwardProp:je}),M=nA;J();var EX=P(L());var sA=P(H());function Y(e){return Nv(e)}J();var iA=["className","elementType","ownerState","externalForwardedProps","getSlotOwnerState","internalForwardedProps"],aA=["component","slots","slotProps"],lA=["component"];function sm(e,t){let{className:r,elementType:o,ownerState:n,externalForwardedProps:s,getSlotOwnerState:i,internalForwardedProps:a}=t,l=k(t,iA),{component:p,slots:c={[e]:void 0},slotProps:u={[e]:void 0}}=s,f=k(s,aA),v=c[e]||o,x=pc(u[e],n),h=lc(d({className:r},l,{externalForwardedProps:e==="root"?f:void 0,externalSlotProps:x})),{props:{component:b},internalRef:y}=h,m=k(h.props,lA),g=yt(y,x?.ref,t.ref),T=i?i(m):{},w=d({},n,T),$=e==="root"?b||p:b,C=mn(v,d({},e==="root"&&!p&&!c[e]&&a,e!=="root"&&!c[e]&&a,m,$&&{as:$},{ref:g}),w);return Object.keys(T).forEach(_=>{delete C[_]}),[v,C]}var D_=P(ui()),I=D_.default;J();var A_=P(L());var Cx=P($r());var pA=e=>{let t;return e<1?t=5.11916*e**2:t=4.5*Math.log(e+1)+2,(t/100).toFixed(2)},Px=pA;var cA=P(L());function pr(){let e=Mn(fl);return e[Ho]||e}function L_(e){return K("MuiPaper",e)}var YX=W("MuiPaper",["root","rounded","outlined","elevation","elevation0","elevation1","elevation2","elevation3","elevation4","elevation5","elevation6","elevation7","elevation8","elevation9","elevation10","elevation11","elevation12","elevation13","elevation14","elevation15","elevation16","elevation17","elevation18","elevation19","elevation20","elevation21","elevation22","elevation23","elevation24"]);var z_=P(H()),uA=["className","component","elevation","square","variant"],dA=e=>{let{square:t,elevation:r,variant:o,classes:n}=e,s={root:["root",o,!t&&"rounded",o==="elevation"&&`elevation${r}`]};return G(s,L_,n)},fA=M("div",{name:"MuiPaper",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[r.variant],!r.square&&t.rounded,r.variant==="elevation"&&t[`elevation${r.elevation}`]]}})(({theme:e,ownerState:t})=>{var r;return d({backgroundColor:(e.vars||e).palette.background.paper,color:(e.vars||e).palette.text.primary,transition:e.transitions.create("box-shadow")},!t.square&&{borderRadius:e.shape.borderRadius},t.variant==="outlined"&&{border:`1px solid ${(e.vars||e).palette.divider}`},t.variant==="elevation"&&d({boxShadow:(e.vars||e).shadows[t.elevation]},!e.vars&&e.palette.mode==="dark"&&{backgroundImage:`linear-gradient(${(0,Cx.alpha)("#fff",Px(t.elevation))}, ${(0,Cx.alpha)("#fff",Px(t.elevation))})`},e.vars&&{backgroundImage:(r=e.vars.overlays)==null?void 0:r[t.elevation]}))}),mA=A_.forwardRef(function(t,r){let o=Y({props:t,name:"MuiPaper"}),{className:n,component:s="div",elevation:i=1,square:a=!1,variant:l="elevation"}=o,p=k(o,uA),c=d({},o,{component:s,elevation:i,square:a,variant:l}),u=dA(c);return(0,z_.jsx)(fA,d({as:s,ownerState:c,className:A(u.root,n),ref:r},p))}),cr=mA;function B_(e){return K("MuiAlert",e)}var yA=W("MuiAlert",["root","action","icon","message","filled","colorSuccess","colorInfo","colorWarning","colorError","filledSuccess","filledInfo","filledWarning","filledError","outlined","outlinedSuccess","outlinedInfo","outlinedWarning","outlinedError","standard","standardSuccess","standardInfo","standardWarning","standardError"]),$x=yA;J();var fm=P(L());var Ox=P($r());J();var Fr=P(L());var Qe=yt;var ks=bo;var im=Sf;J();var It=P(L());function am(e,t){return am=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(r,o){return r.__proto__=o,r},am(e,t)}function lm(e,t){e.prototype=Object.create(t.prototype),e.prototype.constructor=e,am(e,t)}var Pc=P(L()),Cc=P(_d());var wx={disabled:!1};var F_=P(L()),hl=F_.default.createContext(null);var U_=function(t){return t.scrollTop};var $c="unmounted",Oi="exited",Ni="entering",vl="entered",_x="exiting",zn=(function(e){lm(t,e);function t(o,n){var s;s=e.call(this,o,n)||this;var i=n,a=i&&!i.isMounting?o.enter:o.appear,l;return s.appearStatus=null,o.in?a?(l=Oi,s.appearStatus=Ni):l=vl:o.unmountOnExit||o.mountOnEnter?l=$c:l=Oi,s.state={status:l},s.nextCallback=null,s}t.getDerivedStateFromProps=function(n,s){var i=n.in;return i&&s.status===$c?{status:Oi}:null};var r=t.prototype;return r.componentDidMount=function(){this.updateStatus(!0,this.appearStatus)},r.componentDidUpdate=function(n){var s=null;if(n!==this.props){var i=this.state.status;this.props.in?i!==Ni&&i!==vl&&(s=Ni):(i===Ni||i===vl)&&(s=_x)}this.updateStatus(!1,s)},r.componentWillUnmount=function(){this.cancelNextCallback()},r.getTimeouts=function(){var n=this.props.timeout,s,i,a;return s=i=a=n,n!=null&&typeof n!="number"&&(s=n.exit,i=n.enter,a=n.appear!==void 0?n.appear:i),{exit:s,enter:i,appear:a}},r.updateStatus=function(n,s){if(n===void 0&&(n=!1),s!==null)if(this.cancelNextCallback(),s===Ni){if(this.props.unmountOnExit||this.props.mountOnEnter){var i=this.props.nodeRef?this.props.nodeRef.current:Cc.default.findDOMNode(this);i&&U_(i)}this.performEnter(n)}else this.performExit();else this.props.unmountOnExit&&this.state.status===Oi&&this.setState({status:$c})},r.performEnter=function(n){var s=this,i=this.props.enter,a=this.context?this.context.isMounting:n,l=this.props.nodeRef?[a]:[Cc.default.findDOMNode(this),a],p=l[0],c=l[1],u=this.getTimeouts(),f=a?u.appear:u.enter;if(!n&&!i||wx.disabled){this.safeSetState({status:vl},function(){s.props.onEntered(p)});return}this.props.onEnter(p,c),this.safeSetState({status:Ni},function(){s.props.onEntering(p,c),s.onTransitionEnd(f,function(){s.safeSetState({status:vl},function(){s.props.onEntered(p,c)})})})},r.performExit=function(){var n=this,s=this.props.exit,i=this.getTimeouts(),a=this.props.nodeRef?void 0:Cc.default.findDOMNode(this);if(!s||wx.disabled){this.safeSetState({status:Oi},function(){n.props.onExited(a)});return}this.props.onExit(a),this.safeSetState({status:_x},function(){n.props.onExiting(a),n.onTransitionEnd(i.exit,function(){n.safeSetState({status:Oi},function(){n.props.onExited(a)})})})},r.cancelNextCallback=function(){this.nextCallback!==null&&(this.nextCallback.cancel(),this.nextCallback=null)},r.safeSetState=function(n,s){s=this.setNextCallback(s),this.setState(n,s)},r.setNextCallback=function(n){var s=this,i=!0;return this.nextCallback=function(a){i&&(i=!1,s.nextCallback=null,n(a))},this.nextCallback.cancel=function(){i=!1},this.nextCallback},r.onTransitionEnd=function(n,s){this.setNextCallback(s);var i=this.props.nodeRef?this.props.nodeRef.current:Cc.default.findDOMNode(this),a=n==null&&!this.props.addEndListener;if(!i||a){setTimeout(this.nextCallback,0);return}if(this.props.addEndListener){var l=this.props.nodeRef?[this.nextCallback]:[i,this.nextCallback],p=l[0],c=l[1];this.props.addEndListener(p,c)}n!=null&&setTimeout(this.nextCallback,n)},r.render=function(){var n=this.state.status;if(n===$c)return null;var s=this.props,i=s.children,a=s.in,l=s.mountOnEnter,p=s.unmountOnExit,c=s.appear,u=s.enter,f=s.exit,v=s.timeout,x=s.addEndListener,h=s.onEnter,b=s.onEntering,y=s.onEntered,m=s.onExit,g=s.onExiting,T=s.onExited,w=s.nodeRef,$=k(s,["children","in","mountOnEnter","unmountOnExit","appear","enter","exit","timeout","addEndListener","onEnter","onEntering","onEntered","onExit","onExiting","onExited","nodeRef"]);return Pc.default.createElement(hl.Provider,{value:null},typeof i=="function"?i(n,$):Pc.default.cloneElement(Pc.default.Children.only(i),$))},t})(Pc.default.Component);zn.contextType=hl;zn.propTypes={};function gl(){}zn.defaultProps={in:!1,mountOnEnter:!1,unmountOnExit:!1,appear:!1,enter:!0,exit:!0,onEnter:gl,onEntering:gl,onEntered:gl,onExit:gl,onExiting:gl,onExited:gl};zn.UNMOUNTED=$c;zn.EXITED=Oi;zn.ENTERING=Ni;zn.ENTERED=vl;zn.EXITING=_x;var Mi=zn;J();function W_(e){if(e===void 0)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}var wc=P(L());var _o=P(L());function pm(e,t){var r=function(s){return t&&(0,_o.isValidElement)(s)?t(s):s},o=Object.create(null);return e&&_o.Children.map(e,function(n){return n}).forEach(function(n){o[n.key]=r(n)}),o}function hA(e,t){e=e||{},t=t||{};function r(c){return c in t?t[c]:e[c]}var o=Object.create(null),n=[];for(var s in e)s in t?n.length&&(o[s]=n,n=[]):n.push(s);var i,a={};for(var l in t){if(o[l])for(i=0;i<o[l].length;i++){var p=o[l][i];a[o[l][i]]=r(p)}a[l]=r(l)}for(i=0;i<n.length;i++)a[n[i]]=r(n[i]);return a}function Ii(e,t,r){return r[t]!=null?r[t]:e.props[t]}function V_(e,t){return pm(e.children,function(r){return(0,_o.cloneElement)(r,{onExited:t.bind(null,r),in:!0,appear:Ii(r,"appear",e),enter:Ii(r,"enter",e),exit:Ii(r,"exit",e)})})}function H_(e,t,r){var o=pm(e.children),n=hA(t,o);return Object.keys(n).forEach(function(s){var i=n[s];if((0,_o.isValidElement)(i)){var a=s in t,l=s in o,p=t[s],c=(0,_o.isValidElement)(p)&&!p.props.in;l&&(!a||c)?n[s]=(0,_o.cloneElement)(i,{onExited:r.bind(null,i),in:!0,exit:Ii(i,"exit",e),enter:Ii(i,"enter",e)}):!l&&a&&!c?n[s]=(0,_o.cloneElement)(i,{in:!1}):l&&a&&(0,_o.isValidElement)(p)&&(n[s]=(0,_o.cloneElement)(i,{onExited:r.bind(null,i),in:p.props.in,exit:Ii(i,"exit",e),enter:Ii(i,"enter",e)}))}}),n}var gA=Object.values||function(e){return Object.keys(e).map(function(t){return e[t]})},vA={component:"div",childFactory:function(t){return t}},Rx=(function(e){lm(t,e);function t(o,n){var s;s=e.call(this,o,n)||this;var i=s.handleExited.bind(W_(s));return s.state={contextValue:{isMounting:!0},handleExited:i,firstRender:!0},s}var r=t.prototype;return r.componentDidMount=function(){this.mounted=!0,this.setState({contextValue:{isMounting:!1}})},r.componentWillUnmount=function(){this.mounted=!1},t.getDerivedStateFromProps=function(n,s){var i=s.children,a=s.handleExited,l=s.firstRender;return{children:l?V_(n,a):H_(n,i,a),firstRender:!1}},r.handleExited=function(n,s){var i=pm(this.props.children);n.key in i||(n.props.onExited&&n.props.onExited(s),this.mounted&&this.setState(function(a){var l=d({},a.children);return delete l[n.key],{children:l}}))},r.render=function(){var n=this.props,s=n.component,i=n.childFactory,a=k(n,["component","childFactory"]),l=this.state.contextValue,p=gA(this.state.children).map(i);return delete a.appear,delete a.enter,delete a.exit,s===null?wc.default.createElement(hl.Provider,{value:l},p):wc.default.createElement(hl.Provider,{value:l},wc.default.createElement(s,a,p))},t})(wc.default.Component);Rx.propTypes={};Rx.defaultProps=vA;var Ex=Rx;var cm=P(L());var Sx=P(H());function xA(e){let{className:t,classes:r,pulsate:o=!1,rippleX:n,rippleY:s,rippleSize:i,in:a,onExited:l,timeout:p}=e,[c,u]=cm.useState(!1),f=A(t,r.ripple,r.rippleVisible,o&&r.ripplePulsate),v={width:i,height:i,top:-(i/2)+s,left:-(i/2)+n},x=A(r.child,c&&r.childLeaving,o&&r.childPulsate);return!a&&!c&&u(!0),cm.useEffect(()=>{if(!a&&l!=null){let h=setTimeout(l,p);return()=>{clearTimeout(h)}}},[l,a,p]),(0,Sx.jsx)("span",{className:f,style:v,children:(0,Sx.jsx)("span",{className:x})})}var q_=xA;var TA=W("MuiTouchRipple",["root","ripple","rippleVisible","ripplePulsate","child","childLeaving","childPulsate"]),to=TA;var um=P(H()),bA=["center","classes","className"],dm=e=>e,K_,G_,Y_,X_,kx=550,PA=80,CA=(0,bt.keyframes)(K_||(K_=dm`
  0% {
    transform: scale(0);
    opacity: 0.1;
  }

  100% {
    transform: scale(1);
    opacity: 0.3;
  }
`)),$A=(0,bt.keyframes)(G_||(G_=dm`
  0% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
`)),wA=(0,bt.keyframes)(Y_||(Y_=dm`
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(0.92);
  }

  100% {
    transform: scale(1);
  }
`)),_A=M("span",{name:"MuiTouchRipple",slot:"Root"})({overflow:"hidden",pointerEvents:"none",position:"absolute",zIndex:0,top:0,right:0,bottom:0,left:0,borderRadius:"inherit"}),RA=M(q_,{name:"MuiTouchRipple",slot:"Ripple"})(X_||(X_=dm`
  opacity: 0;
  position: absolute;

  &.${0} {
    opacity: 0.3;
    transform: scale(1);
    animation-name: ${0};
    animation-duration: ${0}ms;
    animation-timing-function: ${0};
  }

  &.${0} {
    animation-duration: ${0}ms;
  }

  & .${0} {
    opacity: 1;
    display: block;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background-color: currentColor;
  }

  & .${0} {
    opacity: 0;
    animation-name: ${0};
    animation-duration: ${0}ms;
    animation-timing-function: ${0};
  }

  & .${0} {
    position: absolute;
    /* @noflip */
    left: 0px;
    top: 0;
    animation-name: ${0};
    animation-duration: 2500ms;
    animation-timing-function: ${0};
    animation-iteration-count: infinite;
    animation-delay: 200ms;
  }
`),to.rippleVisible,CA,kx,({theme:e})=>e.transitions.easing.easeInOut,to.ripplePulsate,({theme:e})=>e.transitions.duration.shorter,to.child,to.childLeaving,$A,kx,({theme:e})=>e.transitions.easing.easeInOut,to.childPulsate,wA,({theme:e})=>e.transitions.easing.easeInOut),EA=It.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTouchRipple"}),{center:n=!1,classes:s={},className:i}=o,a=k(o,bA),[l,p]=It.useState([]),c=It.useRef(0),u=It.useRef(null);It.useEffect(()=>{u.current&&(u.current(),u.current=null)},[l]);let f=It.useRef(!1),v=Ar(),x=It.useRef(null),h=It.useRef(null),b=It.useCallback(T=>{let{pulsate:w,rippleX:$,rippleY:C,rippleSize:_,cb:S}=T;p(R=>[...R,(0,um.jsx)(RA,{classes:{ripple:A(s.ripple,to.ripple),rippleVisible:A(s.rippleVisible,to.rippleVisible),ripplePulsate:A(s.ripplePulsate,to.ripplePulsate),child:A(s.child,to.child),childLeaving:A(s.childLeaving,to.childLeaving),childPulsate:A(s.childPulsate,to.childPulsate)},timeout:kx,pulsate:w,rippleX:$,rippleY:C,rippleSize:_},c.current)]),c.current+=1,u.current=S},[s]),y=It.useCallback((T={},w={},$=()=>{})=>{let{pulsate:C=!1,center:_=n||w.pulsate,fakeElement:S=!1}=w;if(T?.type==="mousedown"&&f.current){f.current=!1;return}T?.type==="touchstart"&&(f.current=!0);let R=S?null:h.current,j=R?R.getBoundingClientRect():{width:0,height:0,left:0,top:0},U,z,Z;if(_||T===void 0||T.clientX===0&&T.clientY===0||!T.clientX&&!T.touches)U=Math.round(j.width/2),z=Math.round(j.height/2);else{let{clientX:B,clientY:D}=T.touches&&T.touches.length>0?T.touches[0]:T;U=Math.round(B-j.left),z=Math.round(D-j.top)}if(_)Z=Math.sqrt((2*j.width**2+j.height**2)/3),Z%2===0&&(Z+=1);else{let B=Math.max(Math.abs((R?R.clientWidth:0)-U),U)*2+2,D=Math.max(Math.abs((R?R.clientHeight:0)-z),z)*2+2;Z=Math.sqrt(B**2+D**2)}T!=null&&T.touches?x.current===null&&(x.current=()=>{b({pulsate:C,rippleX:U,rippleY:z,rippleSize:Z,cb:$})},v.start(PA,()=>{x.current&&(x.current(),x.current=null)})):b({pulsate:C,rippleX:U,rippleY:z,rippleSize:Z,cb:$})},[n,b,v]),m=It.useCallback(()=>{y({},{pulsate:!0})},[y]),g=It.useCallback((T,w)=>{if(v.clear(),T?.type==="touchend"&&x.current){x.current(),x.current=null,v.start(0,()=>{g(T,w)});return}x.current=null,p($=>$.length>0?$.slice(1):$),u.current=w},[v]);return It.useImperativeHandle(r,()=>({pulsate:m,start:y,stop:g}),[m,y,g]),(0,um.jsx)(_A,d({className:A(to.root,s.root,i),ref:h},a,{children:(0,um.jsx)(Ex,{component:null,exit:!0,children:l})}))}),Q_=EA;function Z_(e){return K("MuiButtonBase",e)}var SA=W("MuiButtonBase",["root","disabled","focusVisible"]),J_=SA;var eR=P(H()),tR=P(H()),kA=["action","centerRipple","children","className","component","disabled","disableRipple","disableTouchRipple","focusRipple","focusVisibleClassName","LinkComponent","onBlur","onClick","onContextMenu","onDragLeave","onFocus","onFocusVisible","onKeyDown","onKeyUp","onMouseDown","onMouseLeave","onMouseUp","onTouchEnd","onTouchMove","onTouchStart","tabIndex","TouchRippleProps","touchRippleRef","type"],OA=e=>{let{disabled:t,focusVisible:r,focusVisibleClassName:o,classes:n}=e,i=G({root:["root",t&&"disabled",r&&"focusVisible"]},Z_,n);return r&&o&&(i.root+=` ${o}`),i},NA=M("button",{name:"MuiButtonBase",slot:"Root",overridesResolver:(e,t)=>t.root})({display:"inline-flex",alignItems:"center",justifyContent:"center",position:"relative",boxSizing:"border-box",WebkitTapHighlightColor:"transparent",backgroundColor:"transparent",outline:0,border:0,margin:0,borderRadius:0,padding:0,cursor:"pointer",userSelect:"none",verticalAlign:"middle",MozAppearance:"none",WebkitAppearance:"none",textDecoration:"none",color:"inherit","&::-moz-focus-inner":{borderStyle:"none"},[`&.${J_.disabled}`]:{pointerEvents:"none",cursor:"default"},"@media print":{colorAdjust:"exact"}}),MA=Fr.forwardRef(function(t,r){let o=Y({props:t,name:"MuiButtonBase"}),{action:n,centerRipple:s=!1,children:i,className:a,component:l="button",disabled:p=!1,disableRipple:c=!1,disableTouchRipple:u=!1,focusRipple:f=!1,LinkComponent:v="a",onBlur:x,onClick:h,onContextMenu:b,onDragLeave:y,onFocus:m,onFocusVisible:g,onKeyDown:T,onKeyUp:w,onMouseDown:$,onMouseLeave:C,onMouseUp:_,onTouchEnd:S,onTouchMove:R,onTouchStart:j,tabIndex:U=0,TouchRippleProps:z,touchRippleRef:Z,type:B}=o,D=k(o,kA),q=Fr.useRef(null),E=Fr.useRef(null),F=Qe(E,Z),{isFocusVisibleRef:ae,onFocus:ye,onBlur:me,ref:te}=im(),[ne,ue]=Fr.useState(!1);p&&ne&&ue(!1),Fr.useImperativeHandle(n,()=>({focusVisible:()=>{ue(!0),q.current.focus()}}),[]);let[he,be]=Fr.useState(!1);Fr.useEffect(()=>{be(!0)},[]);let Te=he&&!c&&!p;Fr.useEffect(()=>{ne&&f&&!c&&he&&E.current.pulsate()},[c,f,ne,he]);function Pe(ce,_t,xn=u){return ks(so=>(_t&&_t(so),!xn&&E.current&&E.current[ce](so),!0))}let Ke=Pe("start",$),N=Pe("stop",b),V=Pe("stop",y),re=Pe("stop",_),de=Pe("stop",ce=>{ne&&ce.preventDefault(),C&&C(ce)}),ge=Pe("start",j),yr=Pe("stop",S),Kt=Pe("stop",R),wt=Pe("stop",ce=>{me(ce),ae.current===!1&&ue(!1),x&&x(ce)},!1),or=ks(ce=>{q.current||(q.current=ce.currentTarget),ye(ce),ae.current===!0&&(ue(!0),g&&g(ce)),m&&m(ce)}),Je=()=>{let ce=q.current;return l&&l!=="button"&&!(ce.tagName==="A"&&ce.href)},Ie=Fr.useRef(!1),Gt=ks(ce=>{f&&!Ie.current&&ne&&E.current&&ce.key===" "&&(Ie.current=!0,E.current.stop(ce,()=>{E.current.start(ce)})),ce.target===ce.currentTarget&&Je()&&ce.key===" "&&ce.preventDefault(),T&&T(ce),ce.target===ce.currentTarget&&Je()&&ce.key==="Enter"&&!p&&(ce.preventDefault(),h&&h(ce))}),vt=ks(ce=>{f&&ce.key===" "&&E.current&&ne&&!ce.defaultPrevented&&(Ie.current=!1,E.current.stop(ce,()=>{E.current.pulsate(ce)})),w&&w(ce),h&&ce.target===ce.currentTarget&&Je()&&ce.key===" "&&!ce.defaultPrevented&&h(ce)}),Oe=l;Oe==="button"&&(D.href||D.to)&&(Oe=v);let Yt={};Oe==="button"?(Yt.type=B===void 0?"button":B,Yt.disabled=p):(!D.href&&!D.to&&(Yt.role="button"),p&&(Yt["aria-disabled"]=p));let hr=Qe(r,te,q),Or=d({},o,{centerRipple:s,component:l,disabled:p,disableRipple:c,disableTouchRipple:u,focusRipple:f,tabIndex:U,focusVisible:ne}),Se=OA(Or);return(0,tR.jsxs)(NA,d({as:Oe,className:A(Se.root,a),ownerState:Or,onBlur:wt,onClick:h,onContextMenu:N,onFocus:or,onKeyDown:Gt,onKeyUp:vt,onMouseDown:Ke,onMouseLeave:de,onMouseUp:re,onDragLeave:V,onTouchEnd:yr,onTouchMove:Kt,onTouchStart:ge,ref:hr,tabIndex:p?-1:U,type:B},Yt,D,{children:[i,Te?(0,eR.jsx)(Q_,d({ref:F,center:s},z)):null]}))}),Ro=MA;function rR(e){return K("MuiIconButton",e)}var IA=W("MuiIconButton",["root","disabled","colorInherit","colorPrimary","colorSecondary","colorError","colorInfo","colorSuccess","colorWarning","edgeStart","edgeEnd","sizeSmall","sizeMedium","sizeLarge"]),oR=IA;var nR=P(H()),jA=["edge","children","className","color","disabled","disableFocusRipple","size"],DA=e=>{let{classes:t,disabled:r,color:o,edge:n,size:s}=e,i={root:["root",r&&"disabled",o!=="default"&&`color${I(o)}`,n&&`edge${I(n)}`,`size${I(s)}`]};return G(i,rR,t)},LA=M(Ro,{name:"MuiIconButton",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.color!=="default"&&t[`color${I(r.color)}`],r.edge&&t[`edge${I(r.edge)}`],t[`size${I(r.size)}`]]}})(({theme:e,ownerState:t})=>d({textAlign:"center",flex:"0 0 auto",fontSize:e.typography.pxToRem(24),padding:8,borderRadius:"50%",overflow:"visible",color:(e.vars||e).palette.action.active,transition:e.transitions.create("background-color",{duration:e.transitions.duration.shortest})},!t.disableRipple&&{"&:hover":{backgroundColor:e.vars?`rgba(${e.vars.palette.action.activeChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Ox.alpha)(e.palette.action.active,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}}},t.edge==="start"&&{marginLeft:t.size==="small"?-3:-12},t.edge==="end"&&{marginRight:t.size==="small"?-3:-12}),({theme:e,ownerState:t})=>{var r;let o=(r=(e.vars||e).palette)==null?void 0:r[t.color];return d({},t.color==="inherit"&&{color:"inherit"},t.color!=="inherit"&&t.color!=="default"&&d({color:o?.main},!t.disableRipple&&{"&:hover":d({},o&&{backgroundColor:e.vars?`rgba(${o.mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Ox.alpha)(o.main,e.palette.action.hoverOpacity)},{"@media (hover: none)":{backgroundColor:"transparent"}})}),t.size==="small"&&{padding:5,fontSize:e.typography.pxToRem(18)},t.size==="large"&&{padding:12,fontSize:e.typography.pxToRem(28)},{[`&.${oR.disabled}`]:{backgroundColor:"transparent",color:(e.vars||e).palette.action.disabled}})}),AA=fm.forwardRef(function(t,r){let o=Y({props:t,name:"MuiIconButton"}),{edge:n=!1,children:s,className:i,color:a="default",disabled:l=!1,disableFocusRipple:p=!1,size:c="medium"}=o,u=k(o,jA),f=d({},o,{edge:n,color:a,disabled:l,disableFocusRipple:p,size:c}),v=DA(f);return(0,nR.jsx)(LA,d({className:A(v.root,i),centerRipple:!0,focusRipple:!p,disabled:l,ref:r},u,{ownerState:f,children:s}))}),Nx=AA;var oJ=P(L());J();var hm=P(L());J();var mm=P(L());function sR(e){return K("MuiSvgIcon",e)}var BZ=W("MuiSvgIcon",["root","colorPrimary","colorSecondary","colorAction","colorError","colorDisabled","fontSizeInherit","fontSizeSmall","fontSizeMedium","fontSizeLarge"]);var iR=P(H()),aR=P(H()),zA=["children","className","color","component","fontSize","htmlColor","inheritViewBox","titleAccess","viewBox"],BA=e=>{let{color:t,fontSize:r,classes:o}=e,n={root:["root",t!=="inherit"&&`color${I(t)}`,`fontSize${I(r)}`]};return G(n,sR,o)},FA=M("svg",{name:"MuiSvgIcon",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.color!=="inherit"&&t[`color${I(r.color)}`],t[`fontSize${I(r.fontSize)}`]]}})(({theme:e,ownerState:t})=>{var r,o,n,s,i,a,l,p,c,u,f,v,x;return{userSelect:"none",width:"1em",height:"1em",display:"inline-block",fill:t.hasSvgAsChild?void 0:"currentColor",flexShrink:0,transition:(r=e.transitions)==null||(o=r.create)==null?void 0:o.call(r,"fill",{duration:(n=e.transitions)==null||(n=n.duration)==null?void 0:n.shorter}),fontSize:{inherit:"inherit",small:((s=e.typography)==null||(i=s.pxToRem)==null?void 0:i.call(s,20))||"1.25rem",medium:((a=e.typography)==null||(l=a.pxToRem)==null?void 0:l.call(a,24))||"1.5rem",large:((p=e.typography)==null||(c=p.pxToRem)==null?void 0:c.call(p,35))||"2.1875rem"}[t.fontSize],color:(u=(f=(e.vars||e).palette)==null||(f=f[t.color])==null?void 0:f.main)!=null?u:{action:(v=(e.vars||e).palette)==null||(v=v.action)==null?void 0:v.active,disabled:(x=(e.vars||e).palette)==null||(x=x.action)==null?void 0:x.disabled,inherit:void 0}[t.color]}}),lR=mm.forwardRef(function(t,r){let o=Y({props:t,name:"MuiSvgIcon"}),{children:n,className:s,color:i="inherit",component:a="svg",fontSize:l="medium",htmlColor:p,inheritViewBox:c=!1,titleAccess:u,viewBox:f="0 0 24 24"}=o,v=k(o,zA),x=mm.isValidElement(n)&&n.type==="svg",h=d({},o,{color:i,component:a,fontSize:l,instanceFontSize:t.fontSize,inheritViewBox:c,viewBox:f,hasSvgAsChild:x}),b={};c||(b.viewBox=f);let y=BA(h);return(0,aR.jsxs)(FA,d({as:a,className:A(y.root,s),focusable:"false",color:p,"aria-hidden":u?void 0:!0,role:u?"img":void 0,ref:r},b,v,x&&n.props,{ownerState:h,children:[x?n.props.children:n,u?(0,iR.jsx)("title",{children:u}):null]}))});lR.muiName="SvgIcon";var ym=lR;var pR=P(H());function Pt(e,t){function r(o,n){return(0,pR.jsx)(ym,d({"data-testid":`${t}Icon`,ref:n},o,{children:e}))}return r.muiName=ym.muiName,hm.memo(hm.forwardRef(r))}var cR=P(H()),uR=Pt((0,cR.jsx)("path",{d:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2, 4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0, 0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"}),"SuccessOutlined");var iJ=P(L());var dR=P(H()),fR=Pt((0,dR.jsx)("path",{d:"M12 5.99L19.53 19H4.47L12 5.99M12 2L1 21h22L12 2zm1 14h-2v2h2v-2zm0-6h-2v4h2v-4z"}),"ReportProblemOutlined");var pJ=P(L());var mR=P(H()),yR=Pt((0,mR.jsx)("path",{d:"M11 15h2v2h-2zm0-8h2v6h-2zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"}),"ErrorOutline");var dJ=P(L());var hR=P(H()),gR=Pt((0,hR.jsx)("path",{d:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20, 12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10, 10 0 0,0 12,2M11,17H13V11H11V17Z"}),"InfoOutlined");var yJ=P(L());var vR=P(H()),xR=Pt((0,vR.jsx)("path",{d:"M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"}),"Close");var Ko=P(H()),CR=P(H()),UA=["action","children","className","closeText","color","components","componentsProps","icon","iconMapping","onClose","role","severity","slotProps","slots","variant"],WA=e=>{let{variant:t,color:r,severity:o,classes:n}=e,s={root:["root",`color${I(r||o)}`,`${t}${I(r||o)}`,`${t}`],icon:["icon"],message:["message"],action:["action"]};return G(s,B_,n)},VA=M(cr,{name:"MuiAlert",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[r.variant],t[`${r.variant}${I(r.color||r.severity)}`]]}})(({theme:e})=>{let t=e.palette.mode==="light"?xl.darken:xl.lighten,r=e.palette.mode==="light"?xl.lighten:xl.darken;return d({},e.typography.body2,{backgroundColor:"transparent",display:"flex",padding:"6px 16px",variants:[...Object.entries(e.palette).filter(([,o])=>o.main&&o.light).map(([o])=>({props:{colorSeverity:o,variant:"standard"},style:{color:e.vars?e.vars.palette.Alert[`${o}Color`]:t(e.palette[o].light,.6),backgroundColor:e.vars?e.vars.palette.Alert[`${o}StandardBg`]:r(e.palette[o].light,.9),[`& .${$x.icon}`]:e.vars?{color:e.vars.palette.Alert[`${o}IconColor`]}:{color:e.palette[o].main}}})),...Object.entries(e.palette).filter(([,o])=>o.main&&o.light).map(([o])=>({props:{colorSeverity:o,variant:"outlined"},style:{color:e.vars?e.vars.palette.Alert[`${o}Color`]:t(e.palette[o].light,.6),border:`1px solid ${(e.vars||e).palette[o].light}`,[`& .${$x.icon}`]:e.vars?{color:e.vars.palette.Alert[`${o}IconColor`]}:{color:e.palette[o].main}}})),...Object.entries(e.palette).filter(([,o])=>o.main&&o.dark).map(([o])=>({props:{colorSeverity:o,variant:"filled"},style:d({fontWeight:e.typography.fontWeightMedium},e.vars?{color:e.vars.palette.Alert[`${o}FilledColor`],backgroundColor:e.vars.palette.Alert[`${o}FilledBg`]}:{backgroundColor:e.palette.mode==="dark"?e.palette[o].dark:e.palette[o].main,color:e.palette.getContrastText(e.palette[o].main)})}))]})}),HA=M("div",{name:"MuiAlert",slot:"Icon",overridesResolver:(e,t)=>t.icon})({marginRight:12,padding:"7px 0",display:"flex",fontSize:22,opacity:.9}),qA=M("div",{name:"MuiAlert",slot:"Message",overridesResolver:(e,t)=>t.message})({padding:"8px 0",minWidth:0,overflow:"auto"}),TR=M("div",{name:"MuiAlert",slot:"Action",overridesResolver:(e,t)=>t.action})({display:"flex",alignItems:"flex-start",padding:"4px 0 0 16px",marginLeft:"auto",marginRight:-8}),bR={success:(0,Ko.jsx)(uR,{fontSize:"inherit"}),warning:(0,Ko.jsx)(fR,{fontSize:"inherit"}),error:(0,Ko.jsx)(yR,{fontSize:"inherit"}),info:(0,Ko.jsx)(gR,{fontSize:"inherit"})},KA=PR.forwardRef(function(t,r){let o=Y({props:t,name:"MuiAlert"}),{action:n,children:s,className:i,closeText:a="Close",color:l,components:p={},componentsProps:c={},icon:u,iconMapping:f=bR,onClose:v,role:x="alert",severity:h="success",slotProps:b={},slots:y={},variant:m="standard"}=o,g=k(o,UA),T=d({},o,{color:l,severity:h,variant:m,colorSeverity:l||h}),w=WA(T),$={slots:d({closeButton:p.CloseButton,closeIcon:p.CloseIcon},y),slotProps:d({},c,b)},[C,_]=sm("closeButton",{elementType:Nx,externalForwardedProps:$,ownerState:T}),[S,R]=sm("closeIcon",{elementType:xR,externalForwardedProps:$,ownerState:T});return(0,CR.jsxs)(VA,d({role:x,elevation:0,ownerState:T,className:A(w.root,i),ref:r},g,{children:[u!==!1?(0,Ko.jsx)(HA,{ownerState:T,className:w.icon,children:u||f[h]||bR[h]}):null,(0,Ko.jsx)(qA,{ownerState:T,className:w.message,children:s}),n!=null?(0,Ko.jsx)(TR,{ownerState:T,className:w.action,children:n}):null,n==null&&v?(0,Ko.jsx)(TR,{ownerState:T,className:w.action,children:(0,Ko.jsx)(C,d({size:"small","aria-label":a,title:a,color:"inherit",onClick:v},_,{children:(0,Ko.jsx)(S,d({fontSize:"small"},R))}))}):null]}))}),Ur=KA;J();var wR=P(L());function $R(e){return K("MuiAppBar",e)}var BJ=W("MuiAppBar",["root","positionFixed","positionAbsolute","positionSticky","positionStatic","positionRelative","colorDefault","colorPrimary","colorSecondary","colorInherit","colorTransparent","colorError","colorInfo","colorSuccess","colorWarning"]);var _R=P(H()),GA=["className","color","enableColorOnDark","position"],YA=e=>{let{color:t,position:r,classes:o}=e,n={root:["root",`color${I(t)}`,`position${I(r)}`]};return G(n,$R,o)},gm=(e,t)=>e?`${e?.replace(")","")}, ${t})`:t,XA=M(cr,{name:"MuiAppBar",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[`position${I(r.position)}`],t[`color${I(r.color)}`]]}})(({theme:e,ownerState:t})=>{let r=e.palette.mode==="light"?e.palette.grey[100]:e.palette.grey[900];return d({display:"flex",flexDirection:"column",width:"100%",boxSizing:"border-box",flexShrink:0},t.position==="fixed"&&{position:"fixed",zIndex:(e.vars||e).zIndex.appBar,top:0,left:"auto",right:0,"@media print":{position:"absolute"}},t.position==="absolute"&&{position:"absolute",zIndex:(e.vars||e).zIndex.appBar,top:0,left:"auto",right:0},t.position==="sticky"&&{position:"sticky",zIndex:(e.vars||e).zIndex.appBar,top:0,left:"auto",right:0},t.position==="static"&&{position:"static"},t.position==="relative"&&{position:"relative"},!e.vars&&d({},t.color==="default"&&{backgroundColor:r,color:e.palette.getContrastText(r)},t.color&&t.color!=="default"&&t.color!=="inherit"&&t.color!=="transparent"&&{backgroundColor:e.palette[t.color].main,color:e.palette[t.color].contrastText},t.color==="inherit"&&{color:"inherit"},e.palette.mode==="dark"&&!t.enableColorOnDark&&{backgroundColor:null,color:null},t.color==="transparent"&&d({backgroundColor:"transparent",color:"inherit"},e.palette.mode==="dark"&&{backgroundImage:"none"})),e.vars&&d({},t.color==="default"&&{"--AppBar-background":t.enableColorOnDark?e.vars.palette.AppBar.defaultBg:gm(e.vars.palette.AppBar.darkBg,e.vars.palette.AppBar.defaultBg),"--AppBar-color":t.enableColorOnDark?e.vars.palette.text.primary:gm(e.vars.palette.AppBar.darkColor,e.vars.palette.text.primary)},t.color&&!t.color.match(/^(default|inherit|transparent)$/)&&{"--AppBar-background":t.enableColorOnDark?e.vars.palette[t.color].main:gm(e.vars.palette.AppBar.darkBg,e.vars.palette[t.color].main),"--AppBar-color":t.enableColorOnDark?e.vars.palette[t.color].contrastText:gm(e.vars.palette.AppBar.darkColor,e.vars.palette[t.color].contrastText)},!["inherit","transparent"].includes(t.color)&&{backgroundColor:"var(--AppBar-background)"},{color:t.color==="inherit"?"inherit":"var(--AppBar-color)"},t.color==="transparent"&&{backgroundImage:"none",backgroundColor:"transparent",color:"inherit"}))}),QA=wR.forwardRef(function(t,r){let o=Y({props:t,name:"MuiAppBar"}),{className:n,color:s="primary",enableColorOnDark:i=!1,position:a="fixed"}=o,l=k(o,GA),p=d({},o,{color:s,position:a,enableColorOnDark:i}),c=YA(p);return(0,_R.jsx)(XA,d({square:!0,component:"header",ownerState:p,elevation:4,className:A(c.root,n,a==="fixed"&&"mui-fixed"),ref:r},l))}),vm=QA;var ZA=W("MuiBox",["root"]),RR=ZA;var JA=Ss(),ez=af({themeId:Ho,defaultTheme:JA,defaultClassName:RR.root,generateClassName:hi.generate}),Ce=ez;J();var Ec=P(L());var Rc=P($r());function ER(e){return K("MuiButton",e)}var tz=W("MuiButton",["root","text","textInherit","textPrimary","textSecondary","textSuccess","textError","textInfo","textWarning","outlined","outlinedInherit","outlinedPrimary","outlinedSecondary","outlinedSuccess","outlinedError","outlinedInfo","outlinedWarning","contained","containedInherit","containedPrimary","containedSecondary","containedSuccess","containedError","containedInfo","containedWarning","disableElevation","focusVisible","disabled","colorInherit","colorPrimary","colorSecondary","colorSuccess","colorError","colorInfo","colorWarning","textSizeSmall","textSizeMedium","textSizeLarge","outlinedSizeSmall","outlinedSizeMedium","outlinedSizeLarge","containedSizeSmall","containedSizeMedium","containedSizeLarge","sizeMedium","sizeSmall","sizeLarge","fullWidth","startIcon","endIcon","icon","iconSizeSmall","iconSizeMedium","iconSizeLarge"]),_c=tz;var SR=P(L()),rz=SR.createContext({}),kR=rz;var OR=P(L()),oz=OR.createContext(void 0),NR=oz;var Mx=P(H()),MR=P(H()),nz=["children","color","component","className","disabled","disableElevation","disableFocusRipple","endIcon","focusVisibleClassName","fullWidth","size","startIcon","type","variant"],sz=e=>{let{color:t,disableElevation:r,fullWidth:o,size:n,variant:s,classes:i}=e,a={root:["root",s,`${s}${I(t)}`,`size${I(n)}`,`${s}Size${I(n)}`,`color${I(t)}`,r&&"disableElevation",o&&"fullWidth"],label:["label"],startIcon:["icon","startIcon",`iconSize${I(n)}`],endIcon:["icon","endIcon",`iconSize${I(n)}`]},l=G(a,ER,i);return d({},i,l)},IR=e=>d({},e.size==="small"&&{"& > *:nth-of-type(1)":{fontSize:18}},e.size==="medium"&&{"& > *:nth-of-type(1)":{fontSize:20}},e.size==="large"&&{"& > *:nth-of-type(1)":{fontSize:22}}),iz=M(Ro,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiButton",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[r.variant],t[`${r.variant}${I(r.color)}`],t[`size${I(r.size)}`],t[`${r.variant}Size${I(r.size)}`],r.color==="inherit"&&t.colorInherit,r.disableElevation&&t.disableElevation,r.fullWidth&&t.fullWidth]}})(({theme:e,ownerState:t})=>{var r,o;let n=e.palette.mode==="light"?e.palette.grey[300]:e.palette.grey[800],s=e.palette.mode==="light"?e.palette.grey.A100:e.palette.grey[700];return d({},e.typography.button,{minWidth:64,padding:"6px 16px",borderRadius:(e.vars||e).shape.borderRadius,transition:e.transitions.create(["background-color","box-shadow","border-color","color"],{duration:e.transitions.duration.short}),"&:hover":d({textDecoration:"none",backgroundColor:e.vars?`rgba(${e.vars.palette.text.primaryChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Rc.alpha)(e.palette.text.primary,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}},t.variant==="text"&&t.color!=="inherit"&&{backgroundColor:e.vars?`rgba(${e.vars.palette[t.color].mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Rc.alpha)(e.palette[t.color].main,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}},t.variant==="outlined"&&t.color!=="inherit"&&{border:`1px solid ${(e.vars||e).palette[t.color].main}`,backgroundColor:e.vars?`rgba(${e.vars.palette[t.color].mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Rc.alpha)(e.palette[t.color].main,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}},t.variant==="contained"&&{backgroundColor:e.vars?e.vars.palette.Button.inheritContainedHoverBg:s,boxShadow:(e.vars||e).shadows[4],"@media (hover: none)":{boxShadow:(e.vars||e).shadows[2],backgroundColor:(e.vars||e).palette.grey[300]}},t.variant==="contained"&&t.color!=="inherit"&&{backgroundColor:(e.vars||e).palette[t.color].dark,"@media (hover: none)":{backgroundColor:(e.vars||e).palette[t.color].main}}),"&:active":d({},t.variant==="contained"&&{boxShadow:(e.vars||e).shadows[8]}),[`&.${_c.focusVisible}`]:d({},t.variant==="contained"&&{boxShadow:(e.vars||e).shadows[6]}),[`&.${_c.disabled}`]:d({color:(e.vars||e).palette.action.disabled},t.variant==="outlined"&&{border:`1px solid ${(e.vars||e).palette.action.disabledBackground}`},t.variant==="contained"&&{color:(e.vars||e).palette.action.disabled,boxShadow:(e.vars||e).shadows[0],backgroundColor:(e.vars||e).palette.action.disabledBackground})},t.variant==="text"&&{padding:"6px 8px"},t.variant==="text"&&t.color!=="inherit"&&{color:(e.vars||e).palette[t.color].main},t.variant==="outlined"&&{padding:"5px 15px",border:"1px solid currentColor"},t.variant==="outlined"&&t.color!=="inherit"&&{color:(e.vars||e).palette[t.color].main,border:e.vars?`1px solid rgba(${e.vars.palette[t.color].mainChannel} / 0.5)`:`1px solid ${(0,Rc.alpha)(e.palette[t.color].main,.5)}`},t.variant==="contained"&&{color:e.vars?e.vars.palette.text.primary:(r=(o=e.palette).getContrastText)==null?void 0:r.call(o,e.palette.grey[300]),backgroundColor:e.vars?e.vars.palette.Button.inheritContainedBg:n,boxShadow:(e.vars||e).shadows[2]},t.variant==="contained"&&t.color!=="inherit"&&{color:(e.vars||e).palette[t.color].contrastText,backgroundColor:(e.vars||e).palette[t.color].main},t.color==="inherit"&&{color:"inherit",borderColor:"currentColor"},t.size==="small"&&t.variant==="text"&&{padding:"4px 5px",fontSize:e.typography.pxToRem(13)},t.size==="large"&&t.variant==="text"&&{padding:"8px 11px",fontSize:e.typography.pxToRem(15)},t.size==="small"&&t.variant==="outlined"&&{padding:"3px 9px",fontSize:e.typography.pxToRem(13)},t.size==="large"&&t.variant==="outlined"&&{padding:"7px 21px",fontSize:e.typography.pxToRem(15)},t.size==="small"&&t.variant==="contained"&&{padding:"4px 10px",fontSize:e.typography.pxToRem(13)},t.size==="large"&&t.variant==="contained"&&{padding:"8px 22px",fontSize:e.typography.pxToRem(15)},t.fullWidth&&{width:"100%"})},({ownerState:e})=>e.disableElevation&&{boxShadow:"none","&:hover":{boxShadow:"none"},[`&.${_c.focusVisible}`]:{boxShadow:"none"},"&:active":{boxShadow:"none"},[`&.${_c.disabled}`]:{boxShadow:"none"}}),az=M("span",{name:"MuiButton",slot:"StartIcon",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.startIcon,t[`iconSize${I(r.size)}`]]}})(({ownerState:e})=>d({display:"inherit",marginRight:8,marginLeft:-4},e.size==="small"&&{marginLeft:-2},IR(e))),lz=M("span",{name:"MuiButton",slot:"EndIcon",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.endIcon,t[`iconSize${I(r.size)}`]]}})(({ownerState:e})=>d({display:"inherit",marginRight:-4,marginLeft:8},e.size==="small"&&{marginRight:-2},IR(e))),pz=Ec.forwardRef(function(t,r){let o=Ec.useContext(kR),n=Ec.useContext(NR),s=dn(o,t),i=Y({props:s,name:"MuiButton"}),{children:a,color:l="primary",component:p="button",className:c,disabled:u=!1,disableElevation:f=!1,disableFocusRipple:v=!1,endIcon:x,focusVisibleClassName:h,fullWidth:b=!1,size:y="medium",startIcon:m,type:g,variant:T="text"}=i,w=k(i,nz),$=d({},i,{color:l,component:p,disabled:u,disableElevation:f,disableFocusRipple:v,fullWidth:b,size:y,type:g,variant:T}),C=sz($),_=m&&(0,Mx.jsx)(az,{className:C.startIcon,ownerState:$,children:m}),S=x&&(0,Mx.jsx)(lz,{className:C.endIcon,ownerState:$,children:x}),R=n||"";return(0,MR.jsxs)(iz,d({ownerState:$,className:A(o.className,C.root,c,R),component:p,disabled:u,focusRipple:!v,focusVisibleClassName:A(C.focusVisible,h),ref:r,type:g},w,{classes:C,children:[_,a,S]}))}),pe=pz;J();var DR=P(L());function jR(e){return K("MuiCard",e)}var Wee=W("MuiCard",["root"]);var LR=P(H()),cz=["className","raised"],uz=e=>{let{classes:t}=e;return G({root:["root"]},jR,t)},dz=M(cr,{name:"MuiCard",slot:"Root",overridesResolver:(e,t)=>t.root})(()=>({overflow:"hidden"})),fz=DR.forwardRef(function(t,r){let o=Y({props:t,name:"MuiCard"}),{className:n,raised:s=!1}=o,i=k(o,cz),a=d({},o,{raised:s}),l=uz(a);return(0,LR.jsx)(dz,d({className:A(l.root,n),elevation:s?8:void 0,ref:r,ownerState:a},i))}),Tl=fz;J();var zR=P(L());function AR(e){return K("MuiCardContent",e)}var ste=W("MuiCardContent",["root"]);var BR=P(H()),mz=["className","component"],yz=e=>{let{classes:t}=e;return G({root:["root"]},AR,t)},hz=M("div",{name:"MuiCardContent",slot:"Root",overridesResolver:(e,t)=>t.root})(()=>({padding:16,"&:last-child":{paddingBottom:24}})),gz=zR.forwardRef(function(t,r){let o=Y({props:t,name:"MuiCardContent"}),{className:n,component:s="div"}=o,i=k(o,mz),a=d({},o,{component:s}),l=yz(a);return(0,BR.jsx)(hz,d({as:s,className:A(l.root,n),ownerState:a,ref:r},i))}),bl=gz;J();var Sc=P(L());var eE=P($r());J();var VR=P(L());var ji=_f;var UR=P(L());var FR=P(L()),vz=FR.createContext(void 0),Pl=vz;function wr(){return UR.useContext(Pl)}function WR(e){return K("PrivateSwitchBase",e)}var wte=W("PrivateSwitchBase",["root","checked","disabled","input","edgeStart","edgeEnd"]);var HR=P(H()),qR=P(H()),xz=["autoFocus","checked","checkedIcon","className","defaultChecked","disabled","disableFocusRipple","edge","icon","id","inputProps","inputRef","name","onBlur","onChange","onFocus","readOnly","required","tabIndex","type","value"],Tz=e=>{let{classes:t,checked:r,disabled:o,edge:n}=e,s={root:["root",r&&"checked",o&&"disabled",n&&`edge${I(n)}`],input:["input"]};return G(s,WR,t)},bz=M(Ro)(({ownerState:e})=>d({padding:9,borderRadius:"50%"},e.edge==="start"&&{marginLeft:e.size==="small"?-3:-12},e.edge==="end"&&{marginRight:e.size==="small"?-3:-12})),Pz=M("input",{shouldForwardProp:je})({cursor:"inherit",position:"absolute",opacity:0,width:"100%",height:"100%",top:0,left:0,margin:0,padding:0,zIndex:1}),Cz=VR.forwardRef(function(t,r){let{autoFocus:o,checked:n,checkedIcon:s,className:i,defaultChecked:a,disabled:l,disableFocusRipple:p=!1,edge:c=!1,icon:u,id:f,inputProps:v,inputRef:x,name:h,onBlur:b,onChange:y,onFocus:m,readOnly:g,required:T=!1,tabIndex:w,type:$,value:C}=t,_=k(t,xz),[S,R]=ji({controlled:n,default:!!a,name:"SwitchBase",state:"checked"}),j=wr(),U=F=>{m&&m(F),j&&j.onFocus&&j.onFocus(F)},z=F=>{b&&b(F),j&&j.onBlur&&j.onBlur(F)},Z=F=>{if(F.nativeEvent.defaultPrevented)return;let ae=F.target.checked;R(ae),y&&y(F,ae)},B=l;j&&typeof B>"u"&&(B=j.disabled);let D=$==="checkbox"||$==="radio",q=d({},t,{checked:S,disabled:B,disableFocusRipple:p,edge:c}),E=Tz(q);return(0,qR.jsxs)(bz,d({component:"span",className:A(E.root,i),centerRipple:!0,focusRipple:!p,disabled:B,tabIndex:null,role:void 0,onFocus:U,onBlur:z,ownerState:q,ref:r},_,{children:[(0,HR.jsx)(Pz,d({autoFocus:o,checked:n,defaultChecked:a,className:E.input,disabled:B,id:D?f:void 0,name:h,onChange:Z,readOnly:g,ref:x,required:T,ownerState:q,tabIndex:w,type:$},$==="checkbox"&&C===void 0?{}:{value:C},v)),S?s:u]}))}),xm=Cz;var Ate=P(L());var KR=P(H()),GR=Pt((0,KR.jsx)("path",{d:"M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"}),"CheckBoxOutlineBlank");var Fte=P(L());var YR=P(H()),XR=Pt((0,YR.jsx)("path",{d:"M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2V5c0-1.1-.89-2-2-2zm-9 14l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"}),"CheckBox");var Vte=P(L());var QR=P(H()),ZR=Pt((0,QR.jsx)("path",{d:"M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2z"}),"IndeterminateCheckBox");function JR(e){return K("MuiCheckbox",e)}var $z=W("MuiCheckbox",["root","checked","disabled","indeterminate","colorPrimary","colorSecondary","sizeSmall","sizeMedium"]),Tm=$z;var kc=P(H()),wz=["checkedIcon","color","icon","indeterminate","indeterminateIcon","inputProps","size","className"],_z=e=>{let{classes:t,indeterminate:r,color:o,size:n}=e,s={root:["root",r&&"indeterminate",`color${I(o)}`,`size${I(n)}`]},i=G(s,JR,t);return d({},t,i)},Rz=M(xm,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiCheckbox",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.indeterminate&&t.indeterminate,t[`size${I(r.size)}`],r.color!=="default"&&t[`color${I(r.color)}`]]}})(({theme:e,ownerState:t})=>d({color:(e.vars||e).palette.text.secondary},!t.disableRipple&&{"&:hover":{backgroundColor:e.vars?`rgba(${t.color==="default"?e.vars.palette.action.activeChannel:e.vars.palette[t.color].mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,eE.alpha)(t.color==="default"?e.palette.action.active:e.palette[t.color].main,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}}},t.color!=="default"&&{[`&.${Tm.checked}, &.${Tm.indeterminate}`]:{color:(e.vars||e).palette[t.color].main},[`&.${Tm.disabled}`]:{color:(e.vars||e).palette.action.disabled}})),Ez=(0,kc.jsx)(XR,{}),Sz=(0,kc.jsx)(GR,{}),kz=(0,kc.jsx)(ZR,{}),Oz=Sc.forwardRef(function(t,r){var o,n;let s=Y({props:t,name:"MuiCheckbox"}),{checkedIcon:i=Ez,color:a="primary",icon:l=Sz,indeterminate:p=!1,indeterminateIcon:c=kz,inputProps:u,size:f="medium",className:v}=s,x=k(s,wz),h=p?c:l,b=p?c:i,y=d({},s,{color:a,indeterminate:p,size:f}),m=_z(y);return(0,kc.jsx)(Rz,d({type:"checkbox",inputProps:d({"data-indeterminate":p},u),icon:Sc.cloneElement(h,{fontSize:(o=h.props.fontSize)!=null?o:f}),checkedIcon:Sc.cloneElement(b,{fontSize:(n=b.props.fontSize)!=null?n:f}),ownerState:y,ref:r,className:A(m.root,v)},x,{classes:m}))}),Os=Oz;J();var ro=P(L());var Go=P($r());var dre=P(L());var tE=P(H()),rE=Pt((0,tE.jsx)("path",{d:"M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"}),"Cancel");function oE(e){return K("MuiChip",e)}var Nz=W("MuiChip",["root","sizeSmall","sizeMedium","colorError","colorInfo","colorPrimary","colorSecondary","colorSuccess","colorWarning","disabled","clickable","clickableColorPrimary","clickableColorSecondary","deletable","deletableColorPrimary","deletableColorSecondary","outlined","filled","outlinedPrimary","outlinedSecondary","filledPrimary","filledSecondary","avatar","avatarSmall","avatarMedium","avatarColorPrimary","avatarColorSecondary","icon","iconSmall","iconMedium","iconColorPrimary","iconColorSecondary","label","labelSmall","labelMedium","deleteIcon","deleteIconSmall","deleteIconMedium","deleteIconColorPrimary","deleteIconColorSecondary","deleteIconOutlinedColorPrimary","deleteIconOutlinedColorSecondary","deleteIconFilledColorPrimary","deleteIconFilledColorSecondary","focusVisible"]),Re=Nz;var Ix=P(H()),sE=P(H()),Mz=["avatar","className","clickable","color","component","deleteIcon","disabled","icon","label","onClick","onDelete","onKeyDown","onKeyUp","size","variant","tabIndex","skipFocusWhenDisabled"],Iz=e=>{let{classes:t,disabled:r,size:o,color:n,iconColor:s,onDelete:i,clickable:a,variant:l}=e,p={root:["root",l,r&&"disabled",`size${I(o)}`,`color${I(n)}`,a&&"clickable",a&&`clickableColor${I(n)}`,i&&"deletable",i&&`deletableColor${I(n)}`,`${l}${I(n)}`],label:["label",`label${I(o)}`],avatar:["avatar",`avatar${I(o)}`,`avatarColor${I(n)}`],icon:["icon",`icon${I(o)}`,`iconColor${I(s)}`],deleteIcon:["deleteIcon",`deleteIcon${I(o)}`,`deleteIconColor${I(n)}`,`deleteIcon${I(l)}Color${I(n)}`]};return G(p,oE,t)},jz=M("div",{name:"MuiChip",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e,{color:o,iconColor:n,clickable:s,onDelete:i,size:a,variant:l}=r;return[{[`& .${Re.avatar}`]:t.avatar},{[`& .${Re.avatar}`]:t[`avatar${I(a)}`]},{[`& .${Re.avatar}`]:t[`avatarColor${I(o)}`]},{[`& .${Re.icon}`]:t.icon},{[`& .${Re.icon}`]:t[`icon${I(a)}`]},{[`& .${Re.icon}`]:t[`iconColor${I(n)}`]},{[`& .${Re.deleteIcon}`]:t.deleteIcon},{[`& .${Re.deleteIcon}`]:t[`deleteIcon${I(a)}`]},{[`& .${Re.deleteIcon}`]:t[`deleteIconColor${I(o)}`]},{[`& .${Re.deleteIcon}`]:t[`deleteIcon${I(l)}Color${I(o)}`]},t.root,t[`size${I(a)}`],t[`color${I(o)}`],s&&t.clickable,s&&o!=="default"&&t[`clickableColor${I(o)})`],i&&t.deletable,i&&o!=="default"&&t[`deletableColor${I(o)}`],t[l],t[`${l}${I(o)}`]]}})(({theme:e,ownerState:t})=>{let r=e.palette.mode==="light"?e.palette.grey[700]:e.palette.grey[300];return d({maxWidth:"100%",fontFamily:e.typography.fontFamily,fontSize:e.typography.pxToRem(13),display:"inline-flex",alignItems:"center",justifyContent:"center",height:32,color:(e.vars||e).palette.text.primary,backgroundColor:(e.vars||e).palette.action.selected,borderRadius:32/2,whiteSpace:"nowrap",transition:e.transitions.create(["background-color","box-shadow"]),cursor:"unset",outline:0,textDecoration:"none",border:0,padding:0,verticalAlign:"middle",boxSizing:"border-box",[`&.${Re.disabled}`]:{opacity:(e.vars||e).palette.action.disabledOpacity,pointerEvents:"none"},[`& .${Re.avatar}`]:{marginLeft:5,marginRight:-6,width:24,height:24,color:e.vars?e.vars.palette.Chip.defaultAvatarColor:r,fontSize:e.typography.pxToRem(12)},[`& .${Re.avatarColorPrimary}`]:{color:(e.vars||e).palette.primary.contrastText,backgroundColor:(e.vars||e).palette.primary.dark},[`& .${Re.avatarColorSecondary}`]:{color:(e.vars||e).palette.secondary.contrastText,backgroundColor:(e.vars||e).palette.secondary.dark},[`& .${Re.avatarSmall}`]:{marginLeft:4,marginRight:-4,width:18,height:18,fontSize:e.typography.pxToRem(10)},[`& .${Re.icon}`]:d({marginLeft:5,marginRight:-6},t.size==="small"&&{fontSize:18,marginLeft:4,marginRight:-4},t.iconColor===t.color&&d({color:e.vars?e.vars.palette.Chip.defaultIconColor:r},t.color!=="default"&&{color:"inherit"})),[`& .${Re.deleteIcon}`]:d({WebkitTapHighlightColor:"transparent",color:e.vars?`rgba(${e.vars.palette.text.primaryChannel} / 0.26)`:(0,Go.alpha)(e.palette.text.primary,.26),fontSize:22,cursor:"pointer",margin:"0 5px 0 -6px","&:hover":{color:e.vars?`rgba(${e.vars.palette.text.primaryChannel} / 0.4)`:(0,Go.alpha)(e.palette.text.primary,.4)}},t.size==="small"&&{fontSize:16,marginRight:4,marginLeft:-4},t.color!=="default"&&{color:e.vars?`rgba(${e.vars.palette[t.color].contrastTextChannel} / 0.7)`:(0,Go.alpha)(e.palette[t.color].contrastText,.7),"&:hover, &:active":{color:(e.vars||e).palette[t.color].contrastText}})},t.size==="small"&&{height:24},t.color!=="default"&&{backgroundColor:(e.vars||e).palette[t.color].main,color:(e.vars||e).palette[t.color].contrastText},t.onDelete&&{[`&.${Re.focusVisible}`]:{backgroundColor:e.vars?`rgba(${e.vars.palette.action.selectedChannel} / calc(${e.vars.palette.action.selectedOpacity} + ${e.vars.palette.action.focusOpacity}))`:(0,Go.alpha)(e.palette.action.selected,e.palette.action.selectedOpacity+e.palette.action.focusOpacity)}},t.onDelete&&t.color!=="default"&&{[`&.${Re.focusVisible}`]:{backgroundColor:(e.vars||e).palette[t.color].dark}})},({theme:e,ownerState:t})=>d({},t.clickable&&{userSelect:"none",WebkitTapHighlightColor:"transparent",cursor:"pointer","&:hover":{backgroundColor:e.vars?`rgba(${e.vars.palette.action.selectedChannel} / calc(${e.vars.palette.action.selectedOpacity} + ${e.vars.palette.action.hoverOpacity}))`:(0,Go.alpha)(e.palette.action.selected,e.palette.action.selectedOpacity+e.palette.action.hoverOpacity)},[`&.${Re.focusVisible}`]:{backgroundColor:e.vars?`rgba(${e.vars.palette.action.selectedChannel} / calc(${e.vars.palette.action.selectedOpacity} + ${e.vars.palette.action.focusOpacity}))`:(0,Go.alpha)(e.palette.action.selected,e.palette.action.selectedOpacity+e.palette.action.focusOpacity)},"&:active":{boxShadow:(e.vars||e).shadows[1]}},t.clickable&&t.color!=="default"&&{[`&:hover, &.${Re.focusVisible}`]:{backgroundColor:(e.vars||e).palette[t.color].dark}}),({theme:e,ownerState:t})=>d({},t.variant==="outlined"&&{backgroundColor:"transparent",border:e.vars?`1px solid ${e.vars.palette.Chip.defaultBorder}`:`1px solid ${e.palette.mode==="light"?e.palette.grey[400]:e.palette.grey[700]}`,[`&.${Re.clickable}:hover`]:{backgroundColor:(e.vars||e).palette.action.hover},[`&.${Re.focusVisible}`]:{backgroundColor:(e.vars||e).palette.action.focus},[`& .${Re.avatar}`]:{marginLeft:4},[`& .${Re.avatarSmall}`]:{marginLeft:2},[`& .${Re.icon}`]:{marginLeft:4},[`& .${Re.iconSmall}`]:{marginLeft:2},[`& .${Re.deleteIcon}`]:{marginRight:5},[`& .${Re.deleteIconSmall}`]:{marginRight:3}},t.variant==="outlined"&&t.color!=="default"&&{color:(e.vars||e).palette[t.color].main,border:`1px solid ${e.vars?`rgba(${e.vars.palette[t.color].mainChannel} / 0.7)`:(0,Go.alpha)(e.palette[t.color].main,.7)}`,[`&.${Re.clickable}:hover`]:{backgroundColor:e.vars?`rgba(${e.vars.palette[t.color].mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Go.alpha)(e.palette[t.color].main,e.palette.action.hoverOpacity)},[`&.${Re.focusVisible}`]:{backgroundColor:e.vars?`rgba(${e.vars.palette[t.color].mainChannel} / ${e.vars.palette.action.focusOpacity})`:(0,Go.alpha)(e.palette[t.color].main,e.palette.action.focusOpacity)},[`& .${Re.deleteIcon}`]:{color:e.vars?`rgba(${e.vars.palette[t.color].mainChannel} / 0.7)`:(0,Go.alpha)(e.palette[t.color].main,.7),"&:hover, &:active":{color:(e.vars||e).palette[t.color].main}}})),Dz=M("span",{name:"MuiChip",slot:"Label",overridesResolver:(e,t)=>{let{ownerState:r}=e,{size:o}=r;return[t.label,t[`label${I(o)}`]]}})(({ownerState:e})=>d({overflow:"hidden",textOverflow:"ellipsis",paddingLeft:12,paddingRight:12,whiteSpace:"nowrap"},e.variant==="outlined"&&{paddingLeft:11,paddingRight:11},e.size==="small"&&{paddingLeft:8,paddingRight:8},e.size==="small"&&e.variant==="outlined"&&{paddingLeft:7,paddingRight:7}));function nE(e){return e.key==="Backspace"||e.key==="Delete"}var Lz=ro.forwardRef(function(t,r){let o=Y({props:t,name:"MuiChip"}),{avatar:n,className:s,clickable:i,color:a="default",component:l,deleteIcon:p,disabled:c=!1,icon:u,label:f,onClick:v,onDelete:x,onKeyDown:h,onKeyUp:b,size:y="medium",variant:m="filled",tabIndex:g,skipFocusWhenDisabled:T=!1}=o,w=k(o,Mz),$=ro.useRef(null),C=Qe($,r),_=F=>{F.stopPropagation(),x&&x(F)},S=F=>{F.currentTarget===F.target&&nE(F)&&F.preventDefault(),h&&h(F)},R=F=>{F.currentTarget===F.target&&(x&&nE(F)?x(F):F.key==="Escape"&&$.current&&$.current.blur()),b&&b(F)},j=i!==!1&&v?!0:i,U=j||x?Ro:l||"div",z=d({},o,{component:U,disabled:c,size:y,color:a,iconColor:ro.isValidElement(u)&&u.props.color||a,onDelete:!!x,clickable:j,variant:m}),Z=Iz(z),B=U===Ro?d({component:l||"div",focusVisibleClassName:Z.focusVisible},x&&{disableRipple:!0}):{},D=null;x&&(D=p&&ro.isValidElement(p)?ro.cloneElement(p,{className:A(p.props.className,Z.deleteIcon),onClick:_}):(0,Ix.jsx)(rE,{className:A(Z.deleteIcon),onClick:_}));let q=null;n&&ro.isValidElement(n)&&(q=ro.cloneElement(n,{className:A(Z.avatar,n.props.className)}));let E=null;return u&&ro.isValidElement(u)&&(E=ro.cloneElement(u,{className:A(Z.icon,u.props.className)})),(0,sE.jsxs)(jz,d({as:U,className:A(Z.root,s),disabled:j&&c?!0:void 0,onClick:v,onKeyDown:S,onKeyUp:R,ref:C,tabIndex:T&&c?-1:g,ownerState:z},B,w,{children:[q||E,(0,Ix.jsx)(Dz,{className:A(Z.label),ownerState:z,children:f}),D]}))}),Fe=Lz;J();var uE=P(L());function iE(e){return K("MuiCircularProgress",e)}var jre=W("MuiCircularProgress",["root","determinate","indeterminate","colorPrimary","colorSecondary","svg","circle","circleDeterminate","circleIndeterminate","circleDisableShrink"]);var bm=P(H()),Az=["className","color","disableShrink","size","style","thickness","value","variant"],Pm=e=>e,aE,lE,pE,cE,Ns=44,zz=(0,bt.keyframes)(aE||(aE=Pm`
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
`)),Bz=(0,bt.keyframes)(lE||(lE=Pm`
  0% {
    stroke-dasharray: 1px, 200px;
    stroke-dashoffset: 0;
  }

  50% {
    stroke-dasharray: 100px, 200px;
    stroke-dashoffset: -15px;
  }

  100% {
    stroke-dasharray: 100px, 200px;
    stroke-dashoffset: -125px;
  }
`)),Fz=e=>{let{classes:t,variant:r,color:o,disableShrink:n}=e,s={root:["root",r,`color${I(o)}`],svg:["svg"],circle:["circle",`circle${I(r)}`,n&&"circleDisableShrink"]};return G(s,iE,t)},Uz=M("span",{name:"MuiCircularProgress",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[r.variant],t[`color${I(r.color)}`]]}})(({ownerState:e,theme:t})=>d({display:"inline-block"},e.variant==="determinate"&&{transition:t.transitions.create("transform")},e.color!=="inherit"&&{color:(t.vars||t).palette[e.color].main}),({ownerState:e})=>e.variant==="indeterminate"&&(0,bt.css)(pE||(pE=Pm`
      animation: ${0} 1.4s linear infinite;
    `),zz)),Wz=M("svg",{name:"MuiCircularProgress",slot:"Svg",overridesResolver:(e,t)=>t.svg})({display:"block"}),Vz=M("circle",{name:"MuiCircularProgress",slot:"Circle",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.circle,t[`circle${I(r.variant)}`],r.disableShrink&&t.circleDisableShrink]}})(({ownerState:e,theme:t})=>d({stroke:"currentColor"},e.variant==="determinate"&&{transition:t.transitions.create("stroke-dashoffset")},e.variant==="indeterminate"&&{strokeDasharray:"80px, 200px",strokeDashoffset:0}),({ownerState:e})=>e.variant==="indeterminate"&&!e.disableShrink&&(0,bt.css)(cE||(cE=Pm`
      animation: ${0} 1.4s ease-in-out infinite;
    `),Bz)),Hz=uE.forwardRef(function(t,r){let o=Y({props:t,name:"MuiCircularProgress"}),{className:n,color:s="primary",disableShrink:i=!1,size:a=40,style:l,thickness:p=3.6,value:c=0,variant:u="indeterminate"}=o,f=k(o,Az),v=d({},o,{color:s,disableShrink:i,size:a,thickness:p,value:c,variant:u}),x=Fz(v),h={},b={},y={};if(u==="determinate"){let m=2*Math.PI*((Ns-p)/2);h.strokeDasharray=m.toFixed(3),y["aria-valuenow"]=Math.round(c),h.strokeDashoffset=`${((100-c)/100*m).toFixed(3)}px`,b.transform="rotate(-90deg)"}return(0,bm.jsx)(Uz,d({className:A(x.root,n),style:d({width:a,height:a},b,l),ownerState:v,ref:r,role:"progressbar"},y,f,{children:(0,bm.jsx)(Wz,{className:x.svg,ownerState:v,viewBox:`${Ns/2} ${Ns/2} ${Ns} ${Ns}`,children:(0,bm.jsx)(Vz,{className:x.circle,style:h,ownerState:v,cx:Ns,cy:Ns,r:(Ns-p)/2,fill:"none",strokeWidth:p})})}))}),Wr=Hz;J();var fE=P(L());J();var Qre=P(L());var dE=P(H());function qz(e){return(0,dE.jsx)(Qa,d({},e,{defaultTheme:fl,themeId:Ho}))}var Oc=qz;var mE=P(H()),yE=P(H()),Kz=(e,t)=>d({WebkitFontSmoothing:"antialiased",MozOsxFontSmoothing:"grayscale",boxSizing:"border-box",WebkitTextSizeAdjust:"100%"},t&&!e.vars&&{colorScheme:e.palette.mode}),Gz=e=>d({color:(e.vars||e).palette.text.primary},e.typography.body1,{backgroundColor:(e.vars||e).palette.background.default,"@media print":{backgroundColor:(e.vars||e).palette.common.white}}),Yz=(e,t=!1)=>{var r;let o={};t&&e.colorSchemes&&Object.entries(e.colorSchemes).forEach(([i,a])=>{var l;o[e.getColorSchemeSelector(i).replace(/\s*&/,"")]={colorScheme:(l=a.palette)==null?void 0:l.mode}});let n=d({html:Kz(e,t),"*, *::before, *::after":{boxSizing:"inherit"},"strong, b":{fontWeight:e.typography.fontWeightBold},body:d({margin:0},Gz(e),{"&::backdrop":{backgroundColor:(e.vars||e).palette.background.default}})},o),s=(r=e.components)==null||(r=r.MuiCssBaseline)==null?void 0:r.styleOverrides;return s&&(n=[n,s]),n};function Xz(e){let t=Y({props:e,name:"MuiCssBaseline"}),{children:r,enableColorScheme:o=!1}=t;return(0,yE.jsxs)(fE.Fragment,{children:[(0,mE.jsx)(Oc,{styles:n=>Yz(n,o)}),r]})}var Cl=Xz;J();var El=P(L());function Qz(e){let t=rt(e);return t.body===e?xo(e).innerWidth>t.documentElement.clientWidth:e.scrollHeight>e.clientHeight}function $l(e,t){t?e.setAttribute("aria-hidden","true"):e.removeAttribute("aria-hidden")}function hE(e){return parseInt(xo(e).getComputedStyle(e).paddingRight,10)||0}function Zz(e){let r=["TEMPLATE","SCRIPT","STYLE","LINK","MAP","META","NOSCRIPT","PICTURE","COL","COLGROUP","PARAM","SLOT","SOURCE","TRACK"].indexOf(e.tagName)!==-1,o=e.tagName==="INPUT"&&e.getAttribute("type")==="hidden";return r||o}function gE(e,t,r,o,n){let s=[t,r,...o];[].forEach.call(e.children,i=>{let a=s.indexOf(i)===-1,l=!Zz(i);a&&l&&$l(i,n)})}function jx(e,t){let r=-1;return e.some((o,n)=>t(o)?(r=n,!0):!1),r}function Jz(e,t){let r=[],o=e.container;if(!t.disableScrollLock){if(Qz(o)){let i=Ti(rt(o));r.push({value:o.style.paddingRight,property:"padding-right",el:o}),o.style.paddingRight=`${hE(o)+i}px`;let a=rt(o).querySelectorAll(".mui-fixed");[].forEach.call(a,l=>{r.push({value:l.style.paddingRight,property:"padding-right",el:l}),l.style.paddingRight=`${hE(l)+i}px`})}let s;if(o.parentNode instanceof DocumentFragment)s=rt(o).body;else{let i=o.parentElement,a=xo(o);s=i?.nodeName==="HTML"&&a.getComputedStyle(i).overflowY==="scroll"?i:o}r.push({value:s.style.overflow,property:"overflow",el:s},{value:s.style.overflowX,property:"overflow-x",el:s},{value:s.style.overflowY,property:"overflow-y",el:s}),s.style.overflow="hidden"}return()=>{r.forEach(({value:s,el:i,property:a})=>{s?i.style.setProperty(a,s):i.style.removeProperty(a)})}}function eB(e){let t=[];return[].forEach.call(e.children,r=>{r.getAttribute("aria-hidden")==="true"&&t.push(r)}),t}var Cm=class{constructor(){this.containers=void 0,this.modals=void 0,this.modals=[],this.containers=[]}add(t,r){let o=this.modals.indexOf(t);if(o!==-1)return o;o=this.modals.length,this.modals.push(t),t.modalRef&&$l(t.modalRef,!1);let n=eB(r);gE(r,t.mount,t.modalRef,n,!0);let s=jx(this.containers,i=>i.container===r);return s!==-1?(this.containers[s].modals.push(t),o):(this.containers.push({modals:[t],container:r,restore:null,hiddenSiblings:n}),o)}mount(t,r){let o=jx(this.containers,s=>s.modals.indexOf(t)!==-1),n=this.containers[o];n.restore||(n.restore=Jz(n,r))}remove(t,r=!0){let o=this.modals.indexOf(t);if(o===-1)return o;let n=jx(this.containers,i=>i.modals.indexOf(t)!==-1),s=this.containers[n];if(s.modals.splice(s.modals.indexOf(t),1),this.modals.splice(o,1),s.modals.length===0)s.restore&&s.restore(),t.modalRef&&$l(t.modalRef,r),gE(s.container,t.mount,t.modalRef,s.hiddenSiblings,!1),this.containers.splice(n,1);else{let i=s.modals[s.modals.length-1];i.modalRef&&$l(i.modalRef,!1)}return o}isTopModal(t){return this.modals.length>0&&this.modals[this.modals.length-1]===t}};J();var wm=P(L());var er=P(L());var Dx=P(H()),vE=P(H()),tB=["input","select","textarea","a[href]","button","[tabindex]","audio[controls]","video[controls]",'[contenteditable]:not([contenteditable="false"])'].join(",");function rB(e){let t=parseInt(e.getAttribute("tabindex")||"",10);return Number.isNaN(t)?e.contentEditable==="true"||(e.nodeName==="AUDIO"||e.nodeName==="VIDEO"||e.nodeName==="DETAILS")&&e.getAttribute("tabindex")===null?0:e.tabIndex:t}function oB(e){if(e.tagName!=="INPUT"||e.type!=="radio"||!e.name)return!1;let t=o=>e.ownerDocument.querySelector(`input[type="radio"]${o}`),r=t(`[name="${e.name}"]:checked`);return r||(r=t(`[name="${e.name}"]`)),r!==e}function nB(e){return!(e.disabled||e.tagName==="INPUT"&&e.type==="hidden"||oB(e))}function sB(e){let t=[],r=[];return Array.from(e.querySelectorAll(tB)).forEach((o,n)=>{let s=rB(o);s===-1||!nB(o)||(s===0?t.push(o):r.push({documentOrder:n,tabIndex:s,node:o}))}),r.sort((o,n)=>o.tabIndex===n.tabIndex?o.documentOrder-n.documentOrder:o.tabIndex-n.tabIndex).map(o=>o.node).concat(t)}function iB(){return!0}function aB(e){let{children:t,disableAutoFocus:r=!1,disableEnforceFocus:o=!1,disableRestoreFocus:n=!1,getTabbable:s=sB,isEnabled:i=iB,open:a}=e,l=er.useRef(!1),p=er.useRef(null),c=er.useRef(null),u=er.useRef(null),f=er.useRef(null),v=er.useRef(!1),x=er.useRef(null),h=yt(Mt(t),x),b=er.useRef(null);er.useEffect(()=>{!a||!x.current||(v.current=!r)},[r,a]),er.useEffect(()=>{if(!a||!x.current)return;let g=rt(x.current);return x.current.contains(g.activeElement)||(x.current.hasAttribute("tabIndex")||x.current.setAttribute("tabIndex","-1"),v.current&&x.current.focus()),()=>{n||(u.current&&u.current.focus&&(l.current=!0,u.current.focus()),u.current=null)}},[a]),er.useEffect(()=>{if(!a||!x.current)return;let g=rt(x.current),T=C=>{b.current=C,!(o||!i()||C.key!=="Tab")&&g.activeElement===x.current&&C.shiftKey&&(l.current=!0,c.current&&c.current.focus())},w=()=>{let C=x.current;if(C===null)return;if(!g.hasFocus()||!i()||l.current){l.current=!1;return}if(C.contains(g.activeElement)||o&&g.activeElement!==p.current&&g.activeElement!==c.current)return;if(g.activeElement!==f.current)f.current=null;else if(f.current!==null)return;if(!v.current)return;let _=[];if((g.activeElement===p.current||g.activeElement===c.current)&&(_=s(x.current)),_.length>0){var S,R;let j=!!((S=b.current)!=null&&S.shiftKey&&((R=b.current)==null?void 0:R.key)==="Tab"),U=_[0],z=_[_.length-1];typeof U!="string"&&typeof z!="string"&&(j?z.focus():U.focus())}else C.focus()};g.addEventListener("focusin",w),g.addEventListener("keydown",T,!0);let $=setInterval(()=>{g.activeElement&&g.activeElement.tagName==="BODY"&&w()},50);return()=>{clearInterval($),g.removeEventListener("focusin",w),g.removeEventListener("keydown",T,!0)}},[r,o,n,i,a,s]);let y=g=>{u.current===null&&(u.current=g.relatedTarget),v.current=!0,f.current=g.target;let T=t.props.onFocus;T&&T(g)},m=g=>{u.current===null&&(u.current=g.relatedTarget),v.current=!0};return(0,vE.jsxs)(er.Fragment,{children:[(0,Dx.jsx)("div",{tabIndex:a?0:-1,onFocus:m,ref:p,"data-testid":"sentinelStart"}),er.cloneElement(t,{ref:h,onFocus:y}),(0,Dx.jsx)("div",{tabIndex:a?0:-1,onFocus:m,ref:c,"data-testid":"sentinelEnd"})]})}var Lx=aB;var Eo=P(L()),xE=P(_d());var Ax=P(H());function lB(e){return typeof e=="function"?e():e}var pB=Eo.forwardRef(function(t,r){let{children:o,container:n,disablePortal:s=!1}=t,[i,a]=Eo.useState(null),l=yt(Eo.isValidElement(o)?Mt(o):null,r);return Nt(()=>{s||a(lB(n)||document.body)},[n,s]),Nt(()=>{if(i&&!s)return $s(r,i),()=>{$s(r,null)}},[r,i,s]),s?Eo.isValidElement(o)?Eo.cloneElement(o,{ref:l}):(0,Ax.jsx)(Eo.Fragment,{children:o}):(0,Ax.jsx)(Eo.Fragment,{children:i&&xE.createPortal(o,i)})}),Nc=pB;J();var PE=P(L());J();var _l=P(L());var wl=e=>e.scrollTop;function Bn(e,t){var r,o;let{timeout:n,easing:s,style:i={}}=e;return{duration:(r=i.transitionDuration)!=null?r:typeof n=="number"?n:n[t.mode]||0,easing:(o=i.transitionTimingFunction)!=null?o:typeof s=="object"?s[t.mode]:s,delay:i.transitionDelay}}var TE=P(H()),cB=["addEndListener","appear","children","easing","in","onEnter","onEntered","onEntering","onExit","onExited","onExiting","style","timeout","TransitionComponent"],uB={entering:{opacity:1},entered:{opacity:1}},dB=_l.forwardRef(function(t,r){let o=pr(),n={enter:o.transitions.duration.enteringScreen,exit:o.transitions.duration.leavingScreen},{addEndListener:s,appear:i=!0,children:a,easing:l,in:p,onEnter:c,onEntered:u,onEntering:f,onExit:v,onExited:x,onExiting:h,style:b,timeout:y=n,TransitionComponent:m=Mi}=t,g=k(t,cB),T=!0,w=_l.useRef(null),$=Qe(w,Mt(a),r),C=B=>D=>{if(B){let q=w.current;D===void 0?B(q):B(q,D)}},_=C(f),S=C((B,D)=>{wl(B);let q=Bn({style:b,timeout:y,easing:l},{mode:"enter"});B.style.webkitTransition=o.transitions.create("opacity",q),B.style.transition=o.transitions.create("opacity",q),c&&c(B,D)}),R=C(u),j=C(h),U=C(B=>{let D=Bn({style:b,timeout:y,easing:l},{mode:"exit"});B.style.webkitTransition=o.transitions.create("opacity",D),B.style.transition=o.transitions.create("opacity",D),v&&v(B)}),z=C(x);return(0,TE.jsx)(m,d({appear:i,in:p,nodeRef:T?w:void 0,onEnter:S,onEntered:R,onEntering:_,onExit:U,onExited:z,onExiting:j,addEndListener:B=>{s&&s(w.current,B)},timeout:y},g,{children:(B,D)=>_l.cloneElement(a,d({style:d({opacity:0,visibility:B==="exited"&&!p?"hidden":void 0},uB[B],b,a.props.style),ref:$},D))}))}),Mc=dB;function bE(e){return K("MuiBackdrop",e)}var Loe=W("MuiBackdrop",["root","invisible"]);var zx=P(H()),fB=["children","className","component","components","componentsProps","invisible","open","slotProps","slots","TransitionComponent","transitionDuration"],mB=e=>{let{classes:t,invisible:r}=e;return G({root:["root",r&&"invisible"]},bE,t)},yB=M("div",{name:"MuiBackdrop",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.invisible&&t.invisible]}})(({ownerState:e})=>d({position:"fixed",display:"flex",alignItems:"center",justifyContent:"center",right:0,bottom:0,top:0,left:0,backgroundColor:"rgba(0, 0, 0, 0.5)",WebkitTapHighlightColor:"transparent"},e.invisible&&{backgroundColor:"transparent"})),hB=PE.forwardRef(function(t,r){var o,n,s;let i=Y({props:t,name:"MuiBackdrop"}),{children:a,className:l,component:p="div",components:c={},componentsProps:u={},invisible:f=!1,open:v,slotProps:x={},slots:h={},TransitionComponent:b=Mc,transitionDuration:y}=i,m=k(i,fB),g=d({},i,{component:p,invisible:f}),T=mB(g),w=(o=x.root)!=null?o:u.root;return(0,zx.jsx)(b,d({in:v,timeout:y},m,{children:(0,zx.jsx)(yB,d({"aria-hidden":!0},w,{as:(n=(s=h.root)!=null?s:c.Root)!=null?n:p,className:A(T.root,l,w?.className),ownerState:d({},g,w?.ownerState),classes:T,ref:r,children:a}))}))}),Ic=hB;J();var So=P(L());function gB(e){return typeof e=="function"?e():e}function vB(e){return e?e.props.hasOwnProperty("in"):!1}var xB=new Cm;function TB(e){let{container:t,disableEscapeKeyDown:r=!1,disableScrollLock:o=!1,manager:n=xB,closeAfterTransition:s=!1,onTransitionEnter:i,onTransitionExited:a,children:l,onClose:p,open:c,rootRef:u}=e,f=So.useRef({}),v=So.useRef(null),x=So.useRef(null),h=yt(x,u),[b,y]=So.useState(!c),m=vB(l),g=!0;(e["aria-hidden"]==="false"||e["aria-hidden"]===!1)&&(g=!1);let T=()=>rt(v.current),w=()=>(f.current.modalRef=x.current,f.current.mount=v.current,f.current),$=()=>{n.mount(w(),{disableScrollLock:o}),x.current&&(x.current.scrollTop=0)},C=bo(()=>{let D=gB(t)||T().body;n.add(w(),D),x.current&&$()}),_=So.useCallback(()=>n.isTopModal(w()),[n]),S=bo(D=>{v.current=D,D&&(c&&_()?$():x.current&&$l(x.current,g))}),R=So.useCallback(()=>{n.remove(w(),g)},[g,n]);So.useEffect(()=>()=>{R()},[R]),So.useEffect(()=>{c?C():(!m||!s)&&R()},[c,R,m,s,C]);let j=D=>q=>{var E;(E=D.onKeyDown)==null||E.call(D,q),!(q.key!=="Escape"||q.which===229||!_())&&(r||(q.stopPropagation(),p&&p(q,"escapeKeyDown")))},U=D=>q=>{var E;(E=D.onClick)==null||E.call(D,q),q.target===q.currentTarget&&p&&p(q,"backdropClick")};return{getRootProps:(D={})=>{let q=_s(e);delete q.onTransitionEnter,delete q.onTransitionExited;let E=d({},q,D);return d({role:"presentation"},E,{onKeyDown:j(E),ref:h})},getBackdropProps:(D={})=>{let q=D;return d({"aria-hidden":!0},q,{onClick:U(q),open:c})},getTransitionProps:()=>{let D=()=>{y(!1),i&&i()},q=()=>{y(!0),a&&a(),s&&R()};return{onEnter:tl(D,l?.props.onEnter),onExited:tl(q,l?.props.onExited)}},rootRef:h,portalRef:S,isTopModal:_,exited:b,hasTransition:m}}var CE=TB;function $E(e){return K("MuiModal",e)}var nne=W("MuiModal",["root","hidden","backdrop"]);var $m=P(H()),wE=P(H()),bB=["BackdropComponent","BackdropProps","classes","className","closeAfterTransition","children","container","component","components","componentsProps","disableAutoFocus","disableEnforceFocus","disableEscapeKeyDown","disablePortal","disableRestoreFocus","disableScrollLock","hideBackdrop","keepMounted","onBackdropClick","onClose","onTransitionEnter","onTransitionExited","open","slotProps","slots","theme"],PB=e=>{let{open:t,exited:r,classes:o}=e;return G({root:["root",!t&&r&&"hidden"],backdrop:["backdrop"]},$E,o)},CB=M("div",{name:"MuiModal",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,!r.open&&r.exited&&t.hidden]}})(({theme:e,ownerState:t})=>d({position:"fixed",zIndex:(e.vars||e).zIndex.modal,right:0,bottom:0,top:0,left:0},!t.open&&t.exited&&{visibility:"hidden"})),$B=M(Ic,{name:"MuiModal",slot:"Backdrop",overridesResolver:(e,t)=>t.backdrop})({zIndex:-1}),wB=wm.forwardRef(function(t,r){var o,n,s,i,a,l;let p=Y({name:"MuiModal",props:t}),{BackdropComponent:c=$B,BackdropProps:u,className:f,closeAfterTransition:v=!1,children:x,container:h,component:b,components:y={},componentsProps:m={},disableAutoFocus:g=!1,disableEnforceFocus:T=!1,disableEscapeKeyDown:w=!1,disablePortal:$=!1,disableRestoreFocus:C=!1,disableScrollLock:_=!1,hideBackdrop:S=!1,keepMounted:R=!1,onBackdropClick:j,open:U,slotProps:z,slots:Z}=p,B=k(p,bB),D=d({},p,{closeAfterTransition:v,disableAutoFocus:g,disableEnforceFocus:T,disableEscapeKeyDown:w,disablePortal:$,disableRestoreFocus:C,disableScrollLock:_,hideBackdrop:S,keepMounted:R}),{getRootProps:q,getBackdropProps:E,getTransitionProps:F,portalRef:ae,isTopModal:ye,exited:me,hasTransition:te}=CE(d({},D,{rootRef:r})),ne=d({},D,{exited:me}),ue=PB(ne),he={};if(x.props.tabIndex===void 0&&(he.tabIndex="-1"),te){let{onEnter:re,onExited:de}=F();he.onEnter=re,he.onExited=de}let be=(o=(n=Z?.root)!=null?n:y.Root)!=null?o:CB,Te=(s=(i=Z?.backdrop)!=null?i:y.Backdrop)!=null?s:c,Pe=(a=z?.root)!=null?a:m.root,Ke=(l=z?.backdrop)!=null?l:m.backdrop,N=zr({elementType:be,externalSlotProps:Pe,externalForwardedProps:B,getSlotProps:q,additionalProps:{ref:r,as:b},ownerState:ne,className:A(f,Pe?.className,ue?.root,!ne.open&&ne.exited&&ue?.hidden)}),V=zr({elementType:Te,externalSlotProps:Ke,additionalProps:u,getSlotProps:re=>E(d({},re,{onClick:de=>{j&&j(de),re!=null&&re.onClick&&re.onClick(de)}})),className:A(Ke?.className,u?.className,ue?.backdrop),ownerState:ne});return!R&&!U&&(!te||me)?null:(0,$m.jsx)(Nc,{ref:ae,container:h,disablePortal:$,children:(0,wE.jsxs)(be,d({},N,{children:[!S&&c?(0,$m.jsx)(Te,d({},V)):null,(0,$m.jsx)(Lx,{disableEnforceFocus:T,disableAutoFocus:g,disableRestoreFocus:C,isEnabled:ye,open:U,children:wm.cloneElement(x,he)})]}))})}),Di=wB;function _E(e){return K("MuiDialog",e)}var _B=W("MuiDialog",["root","scrollPaper","scrollBody","container","paper","paperScrollPaper","paperScrollBody","paperWidthFalse","paperWidthXs","paperWidthSm","paperWidthMd","paperWidthLg","paperWidthXl","paperFullWidth","paperFullScreen"]),_m=_B;var RE=P(L()),RB=RE.createContext({}),Rm=RB;var Rl=P(H()),EB=["aria-describedby","aria-labelledby","BackdropComponent","BackdropProps","children","className","disableEscapeKeyDown","fullScreen","fullWidth","maxWidth","onBackdropClick","onClick","onClose","open","PaperComponent","PaperProps","scroll","TransitionComponent","transitionDuration","TransitionProps"],SB=M(Ic,{name:"MuiDialog",slot:"Backdrop",overrides:(e,t)=>t.backdrop})({zIndex:-1}),kB=e=>{let{classes:t,scroll:r,maxWidth:o,fullWidth:n,fullScreen:s}=e,i={root:["root"],container:["container",`scroll${I(r)}`],paper:["paper",`paperScroll${I(r)}`,`paperWidth${I(String(o))}`,n&&"paperFullWidth",s&&"paperFullScreen"]};return G(i,_E,t)},OB=M(Di,{name:"MuiDialog",slot:"Root",overridesResolver:(e,t)=>t.root})({"@media print":{position:"absolute !important"}}),NB=M("div",{name:"MuiDialog",slot:"Container",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.container,t[`scroll${I(r.scroll)}`]]}})(({ownerState:e})=>d({height:"100%","@media print":{height:"auto"},outline:0},e.scroll==="paper"&&{display:"flex",justifyContent:"center",alignItems:"center"},e.scroll==="body"&&{overflowY:"auto",overflowX:"hidden",textAlign:"center","&::after":{content:'""',display:"inline-block",verticalAlign:"middle",height:"100%",width:"0"}})),MB=M(cr,{name:"MuiDialog",slot:"Paper",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.paper,t[`scrollPaper${I(r.scroll)}`],t[`paperWidth${I(String(r.maxWidth))}`],r.fullWidth&&t.paperFullWidth,r.fullScreen&&t.paperFullScreen]}})(({theme:e,ownerState:t})=>d({margin:32,position:"relative",overflowY:"auto","@media print":{overflowY:"visible",boxShadow:"none"}},t.scroll==="paper"&&{display:"flex",flexDirection:"column",maxHeight:"calc(100% - 64px)"},t.scroll==="body"&&{display:"inline-block",verticalAlign:"middle",textAlign:"left"},!t.maxWidth&&{maxWidth:"calc(100% - 64px)"},t.maxWidth==="xs"&&{maxWidth:e.breakpoints.unit==="px"?Math.max(e.breakpoints.values.xs,444):`max(${e.breakpoints.values.xs}${e.breakpoints.unit}, 444px)`,[`&.${_m.paperScrollBody}`]:{[e.breakpoints.down(Math.max(e.breakpoints.values.xs,444)+64)]:{maxWidth:"calc(100% - 64px)"}}},t.maxWidth&&t.maxWidth!=="xs"&&{maxWidth:`${e.breakpoints.values[t.maxWidth]}${e.breakpoints.unit}`,[`&.${_m.paperScrollBody}`]:{[e.breakpoints.down(e.breakpoints.values[t.maxWidth]+64)]:{maxWidth:"calc(100% - 64px)"}}},t.fullWidth&&{width:"calc(100% - 64px)"},t.fullScreen&&{margin:0,width:"100%",maxWidth:"100%",height:"100%",maxHeight:"none",borderRadius:0,[`&.${_m.paperScrollBody}`]:{margin:0,maxWidth:"100%"}})),IB=El.forwardRef(function(t,r){let o=Y({props:t,name:"MuiDialog"}),n=pr(),s={enter:n.transitions.duration.enteringScreen,exit:n.transitions.duration.leavingScreen},{"aria-describedby":i,"aria-labelledby":a,BackdropComponent:l,BackdropProps:p,children:c,className:u,disableEscapeKeyDown:f=!1,fullScreen:v=!1,fullWidth:x=!1,maxWidth:h="sm",onBackdropClick:b,onClick:y,onClose:m,open:g,PaperComponent:T=cr,PaperProps:w={},scroll:$="paper",TransitionComponent:C=Mc,transitionDuration:_=s,TransitionProps:S}=o,R=k(o,EB),j=d({},o,{disableEscapeKeyDown:f,fullScreen:v,fullWidth:x,maxWidth:h,scroll:$}),U=kB(j),z=El.useRef(),Z=E=>{z.current=E.target===E.currentTarget},B=E=>{y&&y(E),z.current&&(z.current=null,b&&b(E),m&&m(E,"backdropClick"))},D=To(a),q=El.useMemo(()=>({titleId:D}),[D]);return(0,Rl.jsx)(OB,d({className:A(U.root,u),closeAfterTransition:!0,components:{Backdrop:SB},componentsProps:{backdrop:d({transitionDuration:_,as:l},p)},disableEscapeKeyDown:f,onClose:m,open:g,ref:r,onClick:B,ownerState:j},R,{children:(0,Rl.jsx)(C,d({appear:!0,in:g,timeout:_,role:"presentation"},S,{children:(0,Rl.jsx)(NB,{className:A(U.container),onMouseDown:Z,ownerState:j,children:(0,Rl.jsx)(MB,d({as:T,elevation:24,role:"dialog","aria-describedby":i,"aria-labelledby":D},w,{className:A(U.paper,w.className),ownerState:j,children:(0,Rl.jsx)(Rm.Provider,{value:q,children:c})}))})}))}))}),Fn=IB;J();var SE=P(L());function EE(e){return K("MuiDialogActions",e)}var Kne=W("MuiDialogActions",["root","spacing"]);var kE=P(H()),jB=["className","disableSpacing"],DB=e=>{let{classes:t,disableSpacing:r}=e;return G({root:["root",!r&&"spacing"]},EE,t)},LB=M("div",{name:"MuiDialogActions",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,!r.disableSpacing&&t.spacing]}})(({ownerState:e})=>d({display:"flex",alignItems:"center",padding:8,justifyContent:"flex-end",flex:"0 0 auto"},!e.disableSpacing&&{"& > :not(style) ~ :not(style)":{marginLeft:8}})),AB=SE.forwardRef(function(t,r){let o=Y({props:t,name:"MuiDialogActions"}),{className:n,disableSpacing:s=!1}=o,i=k(o,jB),a=d({},o,{disableSpacing:s}),l=DB(a);return(0,kE.jsx)(LB,d({className:A(l.root,n),ownerState:a,ref:r},i))}),Li=AB;J();var IE=P(L());function OE(e){return K("MuiDialogContent",e)}var lse=W("MuiDialogContent",["root","dividers"]);function NE(e){return K("MuiDialogTitle",e)}var zB=W("MuiDialogTitle",["root"]),ME=zB;var jE=P(H()),BB=["className","dividers"],FB=e=>{let{classes:t,dividers:r}=e;return G({root:["root",r&&"dividers"]},OE,t)},UB=M("div",{name:"MuiDialogContent",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.dividers&&t.dividers]}})(({theme:e,ownerState:t})=>d({flex:"1 1 auto",WebkitOverflowScrolling:"touch",overflowY:"auto",padding:"20px 24px"},t.dividers?{padding:"16px 24px",borderTop:`1px solid ${(e.vars||e).palette.divider}`,borderBottom:`1px solid ${(e.vars||e).palette.divider}`}:{[`.${ME.root} + &`]:{paddingTop:0}})),WB=IE.forwardRef(function(t,r){let o=Y({props:t,name:"MuiDialogContent"}),{className:n,dividers:s=!1}=o,i=k(o,BB),a=d({},o,{dividers:s}),l=FB(a);return(0,jE.jsx)(UB,d({className:A(l.root,n),ownerState:a,ref:r},i))}),Un=WB;J();var Em=P(L());J();var AE=P(L());var zE=P(Yf());function DE(e){return K("MuiTypography",e)}var Rse=W("MuiTypography",["root","h1","h2","h3","h4","h5","h6","subtitle1","subtitle2","body1","body2","inherit","button","caption","overline","alignLeft","alignRight","alignCenter","alignJustify","noWrap","gutterBottom","paragraph"]);var BE=P(H()),VB=["align","className","component","gutterBottom","noWrap","paragraph","variant","variantMapping"],HB=e=>{let{align:t,gutterBottom:r,noWrap:o,paragraph:n,variant:s,classes:i}=e,a={root:["root",s,e.align!=="inherit"&&`align${I(t)}`,r&&"gutterBottom",o&&"noWrap",n&&"paragraph"]};return G(a,DE,i)},qB=M("span",{name:"MuiTypography",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.variant&&t[r.variant],r.align!=="inherit"&&t[`align${I(r.align)}`],r.noWrap&&t.noWrap,r.gutterBottom&&t.gutterBottom,r.paragraph&&t.paragraph]}})(({theme:e,ownerState:t})=>d({margin:0},t.variant==="inherit"&&{font:"inherit"},t.variant!=="inherit"&&e.typography[t.variant],t.align!=="inherit"&&{textAlign:t.align},t.noWrap&&{overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"},t.gutterBottom&&{marginBottom:"0.35em"},t.paragraph&&{marginBottom:16})),LE={h1:"h1",h2:"h2",h3:"h3",h4:"h4",h5:"h5",h6:"h6",subtitle1:"h6",subtitle2:"h6",body1:"p",body2:"p",inherit:"p"},KB={primary:"primary.main",textPrimary:"text.primary",secondary:"secondary.main",textSecondary:"text.secondary",error:"error.main"},GB=e=>KB[e]||e,YB=AE.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTypography"}),n=GB(o.color),s=(0,zE.extendSxProp)(d({},o,{color:n})),{align:i="inherit",className:a,component:l,gutterBottom:p=!1,noWrap:c=!1,paragraph:u=!1,variant:f="body1",variantMapping:v=LE}=s,x=k(s,VB),h=d({},s,{align:i,color:n,className:a,component:l,gutterBottom:p,noWrap:c,paragraph:u,variant:f,variantMapping:v}),b=l||(u?"p":v[f]||LE[f])||"span",y=HB(h);return(0,BE.jsx)(qB,d({as:b,ref:r,ownerState:h,className:A(y.root,a)},x))}),ie=YB;var FE=P(H()),XB=["className","id"],QB=e=>{let{classes:t}=e;return G({root:["root"]},NE,t)},ZB=M(ie,{name:"MuiDialogTitle",slot:"Root",overridesResolver:(e,t)=>t.root})({padding:"16px 24px",flex:"0 0 auto"}),JB=Em.forwardRef(function(t,r){let o=Y({props:t,name:"MuiDialogTitle"}),{className:n,id:s}=o,i=k(o,XB),a=o,l=QB(a),{titleId:p=s}=Em.useContext(Rm);return(0,FE.jsx)(ZB,d({component:"h2",className:A(l.root,n),ownerState:a,ref:r,variant:"h6",id:s??p},i))}),Wn=JB;J();var Ol=P(L());J();var Yo=P(L());var Sm=vi;var km=wf;var Ms=rt;var Ai=xo;var Sl=Nt;var UE=To;var WE=P(H()),eF=["addEndListener","appear","children","container","direction","easing","in","onEnter","onEntered","onEntering","onExit","onExited","onExiting","style","timeout","TransitionComponent"];function tF(e,t,r){let o=t.getBoundingClientRect(),n=r&&r.getBoundingClientRect(),s=Ai(t),i;if(t.fakeTransform)i=t.fakeTransform;else{let p=s.getComputedStyle(t);i=p.getPropertyValue("-webkit-transform")||p.getPropertyValue("transform")}let a=0,l=0;if(i&&i!=="none"&&typeof i=="string"){let p=i.split("(")[1].split(")")[0].split(",");a=parseInt(p[4],10),l=parseInt(p[5],10)}return e==="left"?n?`translateX(${n.right+a-o.left}px)`:`translateX(${s.innerWidth+a-o.left}px)`:e==="right"?n?`translateX(-${o.right-n.left-a}px)`:`translateX(-${o.left+o.width-a}px)`:e==="up"?n?`translateY(${n.bottom+l-o.top}px)`:`translateY(${s.innerHeight+l-o.top}px)`:n?`translateY(-${o.top-n.top+o.height-l}px)`:`translateY(-${o.top+o.height-l}px)`}function rF(e){return typeof e=="function"?e():e}function Om(e,t,r){let o=rF(r),n=tF(e,t,o);n&&(t.style.webkitTransform=n,t.style.transform=n)}var oF=Yo.forwardRef(function(t,r){let o=pr(),n={enter:o.transitions.easing.easeOut,exit:o.transitions.easing.sharp},s={enter:o.transitions.duration.enteringScreen,exit:o.transitions.duration.leavingScreen},{addEndListener:i,appear:a=!0,children:l,container:p,direction:c="down",easing:u=n,in:f,onEnter:v,onEntered:x,onEntering:h,onExit:b,onExited:y,onExiting:m,style:g,timeout:T=s,TransitionComponent:w=Mi}=t,$=k(t,eF),C=Yo.useRef(null),_=Qe(Mt(l),C,r),S=E=>F=>{E&&(F===void 0?E(C.current):E(C.current,F))},R=S((E,F)=>{Om(c,E,p),wl(E),v&&v(E,F)}),j=S((E,F)=>{let ae=Bn({timeout:T,style:g,easing:u},{mode:"enter"});E.style.webkitTransition=o.transitions.create("-webkit-transform",d({},ae)),E.style.transition=o.transitions.create("transform",d({},ae)),E.style.webkitTransform="none",E.style.transform="none",h&&h(E,F)}),U=S(x),z=S(m),Z=S(E=>{let F=Bn({timeout:T,style:g,easing:u},{mode:"exit"});E.style.webkitTransition=o.transitions.create("-webkit-transform",F),E.style.transition=o.transitions.create("transform",F),Om(c,E,p),b&&b(E)}),B=S(E=>{E.style.webkitTransition="",E.style.transition="",y&&y(E)}),D=E=>{i&&i(C.current,E)},q=Yo.useCallback(()=>{C.current&&Om(c,C.current,p)},[c,p]);return Yo.useEffect(()=>{if(f||c==="down"||c==="right")return;let E=Sm(()=>{C.current&&Om(c,C.current,p)}),F=Ai(C.current);return F.addEventListener("resize",E),()=>{E.clear(),F.removeEventListener("resize",E)}},[c,f,p]),Yo.useEffect(()=>{f||q()},[f,q]),(0,WE.jsx)(w,d({nodeRef:C,onEnter:R,onEntered:U,onEntering:j,onExit:Z,onExited:B,onExiting:z,addEndListener:D,appear:a,in:f,timeout:T},$,{children:(E,F)=>Yo.cloneElement(l,d({ref:_,style:d({visibility:E==="exited"&&!f?"hidden":void 0},g,l.props.style)},F))}))}),Bx=oF;function VE(e){return K("MuiDrawer",e)}var Eie=W("MuiDrawer",["root","docked","paper","paperAnchorLeft","paperAnchorRight","paperAnchorTop","paperAnchorBottom","paperAnchorDockedLeft","paperAnchorDockedRight","paperAnchorDockedTop","paperAnchorDockedBottom","modal"]);var kl=P(H()),nF=["BackdropProps"],sF=["anchor","BackdropProps","children","className","elevation","hideBackdrop","ModalProps","onClose","open","PaperProps","SlideProps","TransitionComponent","transitionDuration","variant"],qE=(e,t)=>{let{ownerState:r}=e;return[t.root,(r.variant==="permanent"||r.variant==="persistent")&&t.docked,t.modal]},iF=e=>{let{classes:t,anchor:r,variant:o}=e,n={root:["root"],docked:[(o==="permanent"||o==="persistent")&&"docked"],modal:["modal"],paper:["paper",`paperAnchor${I(r)}`,o!=="temporary"&&`paperAnchorDocked${I(r)}`]};return G(n,VE,t)},aF=M(Di,{name:"MuiDrawer",slot:"Root",overridesResolver:qE})(({theme:e})=>({zIndex:(e.vars||e).zIndex.drawer})),HE=M("div",{shouldForwardProp:je,name:"MuiDrawer",slot:"Docked",skipVariantsResolver:!1,overridesResolver:qE})({flex:"0 0 auto"}),lF=M(cr,{name:"MuiDrawer",slot:"Paper",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.paper,t[`paperAnchor${I(r.anchor)}`],r.variant!=="temporary"&&t[`paperAnchorDocked${I(r.anchor)}`]]}})(({theme:e,ownerState:t})=>d({overflowY:"auto",display:"flex",flexDirection:"column",height:"100%",flex:"1 0 auto",zIndex:(e.vars||e).zIndex.drawer,WebkitOverflowScrolling:"touch",position:"fixed",top:0,outline:0},t.anchor==="left"&&{left:0},t.anchor==="top"&&{top:0,left:0,right:0,height:"auto",maxHeight:"100%"},t.anchor==="right"&&{right:0},t.anchor==="bottom"&&{top:"auto",left:0,bottom:0,right:0,height:"auto",maxHeight:"100%"},t.anchor==="left"&&t.variant!=="temporary"&&{borderRight:`1px solid ${(e.vars||e).palette.divider}`},t.anchor==="top"&&t.variant!=="temporary"&&{borderBottom:`1px solid ${(e.vars||e).palette.divider}`},t.anchor==="right"&&t.variant!=="temporary"&&{borderLeft:`1px solid ${(e.vars||e).palette.divider}`},t.anchor==="bottom"&&t.variant!=="temporary"&&{borderTop:`1px solid ${(e.vars||e).palette.divider}`})),KE={left:"right",right:"left",top:"down",bottom:"up"};function pF(e){return["left","right"].indexOf(e)!==-1}function cF({direction:e},t){return e==="rtl"&&pF(t)?KE[t]:t}var uF=Ol.forwardRef(function(t,r){let o=Y({props:t,name:"MuiDrawer"}),n=pr(),s=Rs(),i={enter:n.transitions.duration.enteringScreen,exit:n.transitions.duration.leavingScreen},{anchor:a="left",BackdropProps:l,children:p,className:c,elevation:u=16,hideBackdrop:f=!1,ModalProps:{BackdropProps:v}={},onClose:x,open:h=!1,PaperProps:b={},SlideProps:y,TransitionComponent:m=Bx,transitionDuration:g=i,variant:T="temporary"}=o,w=k(o.ModalProps,nF),$=k(o,sF),C=Ol.useRef(!1);Ol.useEffect(()=>{C.current=!0},[]);let _=cF({direction:s?"rtl":"ltr"},a),R=d({},o,{anchor:a,elevation:u,open:h,variant:T},$),j=iF(R),U=(0,kl.jsx)(lF,d({elevation:T==="temporary"?u:0,square:!0},b,{className:A(j.paper,b.className),ownerState:R,children:p}));if(T==="permanent")return(0,kl.jsx)(HE,d({className:A(j.root,j.docked,c),ownerState:R,ref:r},$,{children:U}));let z=(0,kl.jsx)(m,d({in:h,direction:KE[_],timeout:g,appear:C.current},y,{children:U}));return T==="persistent"?(0,kl.jsx)(HE,d({className:A(j.root,j.docked,c),ownerState:R,ref:r},$,{children:z})):(0,kl.jsx)(aF,d({BackdropProps:d({},l,v,{transitionDuration:g}),className:A(j.root,j.modal,c),open:h,ownerState:R,onClose:x,hideBackdrop:f,ref:r},$,w,{children:z}))}),Nl=uF;J();var tS=P(L());var Mm=P($r());function GE(e){return K("MuiLinearProgress",e)}var Yie=W("MuiLinearProgress",["root","colorPrimary","colorSecondary","determinate","indeterminate","buffer","query","dashed","dashedColorPrimary","dashedColorSecondary","bar","barColorPrimary","barColorSecondary","bar1Indeterminate","bar1Determinate","bar1Buffer","bar2Indeterminate","bar2Buffer"]);var Nm=P(H()),rS=P(H()),dF=["className","color","value","valueBuffer","variant"],Ml=e=>e,YE,XE,QE,ZE,JE,eS,Fx=4,fF=(0,bt.keyframes)(YE||(YE=Ml`
  0% {
    left: -35%;
    right: 100%;
  }

  60% {
    left: 100%;
    right: -90%;
  }

  100% {
    left: 100%;
    right: -90%;
  }
`)),mF=(0,bt.keyframes)(XE||(XE=Ml`
  0% {
    left: -200%;
    right: 100%;
  }

  60% {
    left: 107%;
    right: -8%;
  }

  100% {
    left: 107%;
    right: -8%;
  }
`)),yF=(0,bt.keyframes)(QE||(QE=Ml`
  0% {
    opacity: 1;
    background-position: 0 -23px;
  }

  60% {
    opacity: 0;
    background-position: 0 -23px;
  }

  100% {
    opacity: 1;
    background-position: -200px -23px;
  }
`)),hF=e=>{let{classes:t,variant:r,color:o}=e,n={root:["root",`color${I(o)}`,r],dashed:["dashed",`dashedColor${I(o)}`],bar1:["bar",`barColor${I(o)}`,(r==="indeterminate"||r==="query")&&"bar1Indeterminate",r==="determinate"&&"bar1Determinate",r==="buffer"&&"bar1Buffer"],bar2:["bar",r!=="buffer"&&`barColor${I(o)}`,r==="buffer"&&`color${I(o)}`,(r==="indeterminate"||r==="query")&&"bar2Indeterminate",r==="buffer"&&"bar2Buffer"]};return G(n,GE,t)},Ux=(e,t)=>t==="inherit"?"currentColor":e.vars?e.vars.palette.LinearProgress[`${t}Bg`]:e.palette.mode==="light"?(0,Mm.lighten)(e.palette[t].main,.62):(0,Mm.darken)(e.palette[t].main,.5),gF=M("span",{name:"MuiLinearProgress",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[`color${I(r.color)}`],t[r.variant]]}})(({ownerState:e,theme:t})=>d({position:"relative",overflow:"hidden",display:"block",height:4,zIndex:0,"@media print":{colorAdjust:"exact"},backgroundColor:Ux(t,e.color)},e.color==="inherit"&&e.variant!=="buffer"&&{backgroundColor:"none","&::before":{content:'""',position:"absolute",left:0,top:0,right:0,bottom:0,backgroundColor:"currentColor",opacity:.3}},e.variant==="buffer"&&{backgroundColor:"transparent"},e.variant==="query"&&{transform:"rotate(180deg)"})),vF=M("span",{name:"MuiLinearProgress",slot:"Dashed",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.dashed,t[`dashedColor${I(r.color)}`]]}})(({ownerState:e,theme:t})=>{let r=Ux(t,e.color);return d({position:"absolute",marginTop:0,height:"100%",width:"100%"},e.color==="inherit"&&{opacity:.3},{backgroundImage:`radial-gradient(${r} 0%, ${r} 16%, transparent 42%)`,backgroundSize:"10px 10px",backgroundPosition:"0 -23px"})},(0,bt.css)(ZE||(ZE=Ml`
    animation: ${0} 3s infinite linear;
  `),yF)),xF=M("span",{name:"MuiLinearProgress",slot:"Bar1",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.bar,t[`barColor${I(r.color)}`],(r.variant==="indeterminate"||r.variant==="query")&&t.bar1Indeterminate,r.variant==="determinate"&&t.bar1Determinate,r.variant==="buffer"&&t.bar1Buffer]}})(({ownerState:e,theme:t})=>d({width:"100%",position:"absolute",left:0,bottom:0,top:0,transition:"transform 0.2s linear",transformOrigin:"left",backgroundColor:e.color==="inherit"?"currentColor":(t.vars||t).palette[e.color].main},e.variant==="determinate"&&{transition:`transform .${Fx}s linear`},e.variant==="buffer"&&{zIndex:1,transition:`transform .${Fx}s linear`}),({ownerState:e})=>(e.variant==="indeterminate"||e.variant==="query")&&(0,bt.css)(JE||(JE=Ml`
      width: auto;
      animation: ${0} 2.1s cubic-bezier(0.65, 0.815, 0.735, 0.395) infinite;
    `),fF)),TF=M("span",{name:"MuiLinearProgress",slot:"Bar2",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.bar,t[`barColor${I(r.color)}`],(r.variant==="indeterminate"||r.variant==="query")&&t.bar2Indeterminate,r.variant==="buffer"&&t.bar2Buffer]}})(({ownerState:e,theme:t})=>d({width:"100%",position:"absolute",left:0,bottom:0,top:0,transition:"transform 0.2s linear",transformOrigin:"left"},e.variant!=="buffer"&&{backgroundColor:e.color==="inherit"?"currentColor":(t.vars||t).palette[e.color].main},e.color==="inherit"&&{opacity:.3},e.variant==="buffer"&&{backgroundColor:Ux(t,e.color),transition:`transform .${Fx}s linear`}),({ownerState:e})=>(e.variant==="indeterminate"||e.variant==="query")&&(0,bt.css)(eS||(eS=Ml`
      width: auto;
      animation: ${0} 2.1s cubic-bezier(0.165, 0.84, 0.44, 1) 1.15s infinite;
    `),mF)),bF=tS.forwardRef(function(t,r){let o=Y({props:t,name:"MuiLinearProgress"}),{className:n,color:s="primary",value:i,valueBuffer:a,variant:l="indeterminate"}=o,p=k(o,dF),c=d({},o,{color:s,variant:l}),u=hF(c),f=Rs(),v={},x={bar1:{},bar2:{}};if((l==="determinate"||l==="buffer")&&i!==void 0){v["aria-valuenow"]=Math.round(i),v["aria-valuemin"]=0,v["aria-valuemax"]=100;let h=i-100;f&&(h=-h),x.bar1.transform=`translateX(${h}%)`}if(l==="buffer"&&a!==void 0){let h=(a||0)-100;f&&(h=-h),x.bar2.transform=`translateX(${h}%)`}return(0,rS.jsxs)(gF,d({className:A(u.root,n),ownerState:c,role:"progressbar"},v,{ref:r},p,{children:[l==="buffer"?(0,Nm.jsx)(vF,{className:u.dashed,ownerState:c}):null,(0,Nm.jsx)(xF,{className:u.bar1,ownerState:c,style:x.bar1}),l==="determinate"?null:(0,Nm.jsx)(TF,{className:u.bar2,ownerState:c,style:x.bar2})]}))}),Xo=bF;J();var Is=P(L());var Dc=P($r());var oS=P(L()),PF=oS.createContext({}),jc=PF;var CF=W("MuiDivider",["root","absolute","fullWidth","inset","middle","flexItem","light","vertical","withChildren","withChildrenVertical","textAlignRight","textAlignLeft","wrapper","wrapperVertical"]),Im=CF;var $F=W("MuiListItemIcon",["root","alignItemsFlexStart"]),jm=$F;var wF=W("MuiListItemText",["root","multiline","dense","inset","primary","secondary"]),Dm=wF;function nS(e){return K("MuiMenuItem",e)}var _F=W("MuiMenuItem",["root","focusVisible","dense","disabled","divider","gutters","selected"]),Il=_F;var Wx=P(H()),RF=["autoFocus","component","dense","divider","disableGutters","focusVisibleClassName","role","tabIndex","className"],EF=(e,t)=>{let{ownerState:r}=e;return[t.root,r.dense&&t.dense,r.divider&&t.divider,!r.disableGutters&&t.gutters]},SF=e=>{let{disabled:t,dense:r,divider:o,disableGutters:n,selected:s,classes:i}=e,l=G({root:["root",r&&"dense",t&&"disabled",!n&&"gutters",o&&"divider",s&&"selected"]},nS,i);return d({},i,l)},kF=M(Ro,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiMenuItem",slot:"Root",overridesResolver:EF})(({theme:e,ownerState:t})=>d({},e.typography.body1,{display:"flex",justifyContent:"flex-start",alignItems:"center",position:"relative",textDecoration:"none",minHeight:48,paddingTop:6,paddingBottom:6,boxSizing:"border-box",whiteSpace:"nowrap"},!t.disableGutters&&{paddingLeft:16,paddingRight:16},t.divider&&{borderBottom:`1px solid ${(e.vars||e).palette.divider}`,backgroundClip:"padding-box"},{"&:hover":{textDecoration:"none",backgroundColor:(e.vars||e).palette.action.hover,"@media (hover: none)":{backgroundColor:"transparent"}},[`&.${Il.selected}`]:{backgroundColor:e.vars?`rgba(${e.vars.palette.primary.mainChannel} / ${e.vars.palette.action.selectedOpacity})`:(0,Dc.alpha)(e.palette.primary.main,e.palette.action.selectedOpacity),[`&.${Il.focusVisible}`]:{backgroundColor:e.vars?`rgba(${e.vars.palette.primary.mainChannel} / calc(${e.vars.palette.action.selectedOpacity} + ${e.vars.palette.action.focusOpacity}))`:(0,Dc.alpha)(e.palette.primary.main,e.palette.action.selectedOpacity+e.palette.action.focusOpacity)}},[`&.${Il.selected}:hover`]:{backgroundColor:e.vars?`rgba(${e.vars.palette.primary.mainChannel} / calc(${e.vars.palette.action.selectedOpacity} + ${e.vars.palette.action.hoverOpacity}))`:(0,Dc.alpha)(e.palette.primary.main,e.palette.action.selectedOpacity+e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:e.vars?`rgba(${e.vars.palette.primary.mainChannel} / ${e.vars.palette.action.selectedOpacity})`:(0,Dc.alpha)(e.palette.primary.main,e.palette.action.selectedOpacity)}},[`&.${Il.focusVisible}`]:{backgroundColor:(e.vars||e).palette.action.focus},[`&.${Il.disabled}`]:{opacity:(e.vars||e).palette.action.disabledOpacity},[`& + .${Im.root}`]:{marginTop:e.spacing(1),marginBottom:e.spacing(1)},[`& + .${Im.inset}`]:{marginLeft:52},[`& .${Dm.root}`]:{marginTop:0,marginBottom:0},[`& .${Dm.inset}`]:{paddingLeft:36},[`& .${jm.root}`]:{minWidth:36}},!t.dense&&{[e.breakpoints.up("sm")]:{minHeight:"auto"}},t.dense&&d({minHeight:32,paddingTop:4,paddingBottom:4},e.typography.body2,{[`& .${jm.root} svg`]:{fontSize:"1.25rem"}}))),OF=Is.forwardRef(function(t,r){let o=Y({props:t,name:"MuiMenuItem"}),{autoFocus:n=!1,component:s="li",dense:i=!1,divider:a=!1,disableGutters:l=!1,focusVisibleClassName:p,role:c="menuitem",tabIndex:u,className:f}=o,v=k(o,RF),x=Is.useContext(jc),h=Is.useMemo(()=>({dense:i||x.dense||!1,disableGutters:l}),[x.dense,i,l]),b=Is.useRef(null);Sl(()=>{n&&b.current&&b.current.focus()},[n]);let y=d({},o,{dense:h.dense,divider:a,disableGutters:l}),m=SF(o),g=Qe(b,r),T;return o.disabled||(T=u!==void 0?u:-1),(0,Wx.jsx)(jc.Provider,{value:h,children:(0,Wx.jsx)(kF,d({ref:g,role:c,tabIndex:T,component:s,focusVisibleClassName:A(m.focusVisible,p),className:A(m.root,f)},v,{ownerState:y,classes:m}))})}),dt=OF;J();var Lm=P(L());J();var jl=P(L());function NF(e={}){let{autoHideDuration:t=null,disableWindowBlurListener:r=!1,onClose:o,open:n,resumeHideDuration:s}=e,i=Ar();jl.useEffect(()=>{if(!n)return;function y(m){m.defaultPrevented||(m.key==="Escape"||m.key==="Esc")&&o?.(m,"escapeKeyDown")}return document.addEventListener("keydown",y),()=>{document.removeEventListener("keydown",y)}},[n,o]);let a=bo((y,m)=>{o?.(y,m)}),l=bo(y=>{!o||y==null||i.start(y,()=>{a(null,"timeout")})});jl.useEffect(()=>(n&&l(t),i.clear),[n,t,l,i]);let p=y=>{o?.(y,"clickaway")},c=i.clear,u=jl.useCallback(()=>{t!=null&&l(s??t*.5)},[t,s,l]),f=y=>m=>{let g=y.onBlur;g?.(m),u()},v=y=>m=>{let g=y.onFocus;g?.(m),c()},x=y=>m=>{let g=y.onMouseEnter;g?.(m),c()},h=y=>m=>{let g=y.onMouseLeave;g?.(m),u()};return jl.useEffect(()=>{if(!r&&n)return window.addEventListener("focus",u),window.addEventListener("blur",c),()=>{window.removeEventListener("focus",u),window.removeEventListener("blur",c)}},[r,n,u,c]),{getRootProps:(y={})=>{let m=d({},_s(e),_s(y));return d({role:"presentation"},y,m,{onBlur:f(m),onFocus:v(m),onMouseEnter:x(m),onMouseLeave:h(m)})},onClickAway:p}}var sS=NF;var oo=P(L());var aS=P(H());function iS(e){return e.substring(2).toLowerCase()}function MF(e,t){return t.documentElement.clientWidth<e.clientX||t.documentElement.clientHeight<e.clientY}function Vx(e){let{children:t,disableReactTree:r=!1,mouseEvent:o="onClick",onClickAway:n,touchEvent:s="onTouchEnd"}=e,i=oo.useRef(!1),a=oo.useRef(null),l=oo.useRef(!1),p=oo.useRef(!1);oo.useEffect(()=>(setTimeout(()=>{l.current=!0},0),()=>{l.current=!1}),[]);let c=yt(Mt(t),a),u=bo(x=>{let h=p.current;p.current=!1;let b=rt(a.current);if(!l.current||!a.current||"clientX"in x&&MF(x,b))return;if(i.current){i.current=!1;return}let y;x.composedPath?y=x.composedPath().indexOf(a.current)>-1:y=!b.documentElement.contains(x.target)||a.current.contains(x.target),!y&&(r||!h)&&n(x)}),f=x=>h=>{p.current=!0;let b=t.props[x];b&&b(h)},v={ref:c};return s!==!1&&(v[s]=f(s)),oo.useEffect(()=>{if(s!==!1){let x=iS(s),h=rt(a.current),b=()=>{i.current=!0};return h.addEventListener(x,u),h.addEventListener("touchmove",b),()=>{h.removeEventListener(x,u),h.removeEventListener("touchmove",b)}}},[u,s]),o!==!1&&(v[o]=f(o)),oo.useEffect(()=>{if(o!==!1){let x=iS(o),h=rt(a.current);return h.addEventListener(x,u),()=>{h.removeEventListener(x,u)}}},[u,o]),(0,aS.jsx)(oo.Fragment,{children:oo.cloneElement(t,v)})}J();var zi=P(L());var lS=P(H()),IF=["addEndListener","appear","children","easing","in","onEnter","onEntered","onEntering","onExit","onExited","onExiting","style","timeout","TransitionComponent"];function qx(e){return`scale(${e}, ${e**2})`}var jF={entering:{opacity:1,transform:qx(1)},entered:{opacity:1,transform:"none"}},Hx=typeof navigator<"u"&&/^((?!chrome|android).)*(safari|mobile)/i.test(navigator.userAgent)&&/(os |version\/)15(.|_)4/i.test(navigator.userAgent),pS=zi.forwardRef(function(t,r){let{addEndListener:o,appear:n=!0,children:s,easing:i,in:a,onEnter:l,onEntered:p,onEntering:c,onExit:u,onExited:f,onExiting:v,style:x,timeout:h="auto",TransitionComponent:b=Mi}=t,y=k(t,IF),m=Ar(),g=zi.useRef(),T=pr(),w=zi.useRef(null),$=Qe(w,Mt(s),r),C=B=>D=>{if(B){let q=w.current;D===void 0?B(q):B(q,D)}},_=C(c),S=C((B,D)=>{wl(B);let{duration:q,delay:E,easing:F}=Bn({style:x,timeout:h,easing:i},{mode:"enter"}),ae;h==="auto"?(ae=T.transitions.getAutoHeightDuration(B.clientHeight),g.current=ae):ae=q,B.style.transition=[T.transitions.create("opacity",{duration:ae,delay:E}),T.transitions.create("transform",{duration:Hx?ae:ae*.666,delay:E,easing:F})].join(","),l&&l(B,D)}),R=C(p),j=C(v),U=C(B=>{let{duration:D,delay:q,easing:E}=Bn({style:x,timeout:h,easing:i},{mode:"exit"}),F;h==="auto"?(F=T.transitions.getAutoHeightDuration(B.clientHeight),g.current=F):F=D,B.style.transition=[T.transitions.create("opacity",{duration:F,delay:q}),T.transitions.create("transform",{duration:Hx?F:F*.666,delay:Hx?q:q||F*.333,easing:E})].join(","),B.style.opacity=0,B.style.transform=qx(.75),u&&u(B)}),z=C(f);return(0,lS.jsx)(b,d({appear:n,in:a,nodeRef:w,onEnter:S,onEntered:R,onEntering:_,onExit:U,onExited:z,onExiting:j,addEndListener:B=>{h==="auto"&&m.start(g.current||0,B),o&&o(w.current,B)},timeout:h==="auto"?null:h},y,{children:(B,D)=>zi.cloneElement(s,d({style:d({opacity:0,transform:qx(.75),visibility:B==="exited"&&!a?"hidden":void 0},jF[B],x,s.props.style),ref:$},D))}))});pS.muiSupportAuto=!0;var js=pS;J();var uS=P(L());var dS=P($r());function cS(e){return K("MuiSnackbarContent",e)}var vle=W("MuiSnackbarContent",["root","message","action"]);var Kx=P(H()),fS=P(H()),DF=["action","className","message","role"],LF=e=>{let{classes:t}=e;return G({root:["root"],action:["action"],message:["message"]},cS,t)},AF=M(cr,{name:"MuiSnackbarContent",slot:"Root",overridesResolver:(e,t)=>t.root})(({theme:e})=>{let t=e.palette.mode==="light"?.8:.98,r=(0,dS.emphasize)(e.palette.background.default,t);return d({},e.typography.body2,{color:e.vars?e.vars.palette.SnackbarContent.color:e.palette.getContrastText(r),backgroundColor:e.vars?e.vars.palette.SnackbarContent.bg:r,display:"flex",alignItems:"center",flexWrap:"wrap",padding:"6px 16px",borderRadius:(e.vars||e).shape.borderRadius,flexGrow:1,[e.breakpoints.up("sm")]:{flexGrow:"initial",minWidth:288}})}),zF=M("div",{name:"MuiSnackbarContent",slot:"Message",overridesResolver:(e,t)=>t.message})({padding:"8px 0"}),BF=M("div",{name:"MuiSnackbarContent",slot:"Action",overridesResolver:(e,t)=>t.action})({display:"flex",alignItems:"center",marginLeft:"auto",paddingLeft:16,marginRight:-8}),FF=uS.forwardRef(function(t,r){let o=Y({props:t,name:"MuiSnackbarContent"}),{action:n,className:s,message:i,role:a="alert"}=o,l=k(o,DF),p=o,c=LF(p);return(0,fS.jsxs)(AF,d({role:a,square:!0,elevation:6,className:A(c.root,s),ownerState:p,ref:r},l,{children:[(0,Kx.jsx)(zF,{className:c.message,ownerState:p,children:i}),n?(0,Kx.jsx)(BF,{className:c.action,ownerState:p,children:n}):null]}))}),Gx=FF;function mS(e){return K("MuiSnackbar",e)}var Ile=W("MuiSnackbar",["root","anchorOriginTopCenter","anchorOriginBottomCenter","anchorOriginTopRight","anchorOriginBottomRight","anchorOriginTopLeft","anchorOriginBottomLeft"]);var Lc=P(H()),UF=["onEnter","onExited"],WF=["action","anchorOrigin","autoHideDuration","children","className","ClickAwayListenerProps","ContentProps","disableWindowBlurListener","message","onBlur","onClose","onFocus","onMouseEnter","onMouseLeave","open","resumeHideDuration","TransitionComponent","transitionDuration","TransitionProps"],VF=e=>{let{classes:t,anchorOrigin:r}=e,o={root:["root",`anchorOrigin${I(r.vertical)}${I(r.horizontal)}`]};return G(o,mS,t)},yS=M("div",{name:"MuiSnackbar",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[`anchorOrigin${I(r.anchorOrigin.vertical)}${I(r.anchorOrigin.horizontal)}`]]}})(({theme:e,ownerState:t})=>{let r={left:"50%",right:"auto",transform:"translateX(-50%)"};return d({zIndex:(e.vars||e).zIndex.snackbar,position:"fixed",display:"flex",left:8,right:8,justifyContent:"center",alignItems:"center"},t.anchorOrigin.vertical==="top"?{top:8}:{bottom:8},t.anchorOrigin.horizontal==="left"&&{justifyContent:"flex-start"},t.anchorOrigin.horizontal==="right"&&{justifyContent:"flex-end"},{[e.breakpoints.up("sm")]:d({},t.anchorOrigin.vertical==="top"?{top:24}:{bottom:24},t.anchorOrigin.horizontal==="center"&&r,t.anchorOrigin.horizontal==="left"&&{left:24,right:"auto"},t.anchorOrigin.horizontal==="right"&&{right:24,left:"auto"})})}),HF=Lm.forwardRef(function(t,r){let o=Y({props:t,name:"MuiSnackbar"}),n=pr(),s={enter:n.transitions.duration.enteringScreen,exit:n.transitions.duration.leavingScreen},{action:i,anchorOrigin:{vertical:a,horizontal:l}={vertical:"bottom",horizontal:"left"},autoHideDuration:p=null,children:c,className:u,ClickAwayListenerProps:f,ContentProps:v,disableWindowBlurListener:x=!1,message:h,open:b,TransitionComponent:y=js,transitionDuration:m=s,TransitionProps:{onEnter:g,onExited:T}={}}=o,w=k(o.TransitionProps,UF),$=k(o,WF),C=d({},o,{anchorOrigin:{vertical:a,horizontal:l},autoHideDuration:p,disableWindowBlurListener:x,TransitionComponent:y,transitionDuration:m}),_=VF(C),{getRootProps:S,onClickAway:R}=sS(d({},C)),[j,U]=Lm.useState(!0),z=zr({elementType:yS,getSlotProps:S,externalForwardedProps:$,ownerState:C,additionalProps:{ref:r},className:[_.root,u]}),Z=D=>{U(!0),T&&T(D)},B=(D,q)=>{U(!1),g&&g(D,q)};return!b&&j?null:(0,Lc.jsx)(Vx,d({onClickAway:R},f,{children:(0,Lc.jsx)(yS,d({},z,{children:(0,Lc.jsx)(y,d({appear:!0,in:b,timeout:m,direction:a==="top"?"down":"up",onEnter:B,onExited:Z},w,{children:c||(0,Lc.jsx)(Gx,d({message:h,action:i},v))}))}))}))}),Am=HF;var qF=Af({createStyledComponent:M("div",{name:"MuiStack",slot:"Root",overridesResolver:(e,t)=>t.root}),useThemeProps:e=>Y({props:e,name:"MuiStack"})}),Ee=qF;J();var gS=P(L());var Bi=P($r());function hS(e){return K("MuiSwitch",e)}var KF=W("MuiSwitch",["root","edgeStart","edgeEnd","switchBase","colorPrimary","colorSecondary","sizeSmall","sizeMedium","checked","disabled","input","thumb","track"]),ur=KF;var zm=P(H()),vS=P(H()),GF=["className","color","edge","size","sx"],YF=e=>{let{classes:t,edge:r,size:o,color:n,checked:s,disabled:i}=e,a={root:["root",r&&`edge${I(r)}`,`size${I(o)}`],switchBase:["switchBase",`color${I(n)}`,s&&"checked",i&&"disabled"],thumb:["thumb"],track:["track"],input:["input"]},l=G(a,hS,t);return d({},t,l)},XF=M("span",{name:"MuiSwitch",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.edge&&t[`edge${I(r.edge)}`],t[`size${I(r.size)}`]]}})({display:"inline-flex",width:58,height:38,overflow:"hidden",padding:12,boxSizing:"border-box",position:"relative",flexShrink:0,zIndex:0,verticalAlign:"middle","@media print":{colorAdjust:"exact"},variants:[{props:{edge:"start"},style:{marginLeft:-8}},{props:{edge:"end"},style:{marginRight:-8}},{props:{size:"small"},style:{width:40,height:24,padding:7,[`& .${ur.thumb}`]:{width:16,height:16},[`& .${ur.switchBase}`]:{padding:4,[`&.${ur.checked}`]:{transform:"translateX(16px)"}}}}]}),QF=M(xm,{name:"MuiSwitch",slot:"SwitchBase",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.switchBase,{[`& .${ur.input}`]:t.input},r.color!=="default"&&t[`color${I(r.color)}`]]}})(({theme:e})=>({position:"absolute",top:0,left:0,zIndex:1,color:e.vars?e.vars.palette.Switch.defaultColor:`${e.palette.mode==="light"?e.palette.common.white:e.palette.grey[300]}`,transition:e.transitions.create(["left","transform"],{duration:e.transitions.duration.shortest}),[`&.${ur.checked}`]:{transform:"translateX(20px)"},[`&.${ur.disabled}`]:{color:e.vars?e.vars.palette.Switch.defaultDisabledColor:`${e.palette.mode==="light"?e.palette.grey[100]:e.palette.grey[600]}`},[`&.${ur.checked} + .${ur.track}`]:{opacity:.5},[`&.${ur.disabled} + .${ur.track}`]:{opacity:e.vars?e.vars.opacity.switchTrackDisabled:`${e.palette.mode==="light"?.12:.2}`},[`& .${ur.input}`]:{left:"-100%",width:"300%"}}),({theme:e})=>({"&:hover":{backgroundColor:e.vars?`rgba(${e.vars.palette.action.activeChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Bi.alpha)(e.palette.action.active,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}},variants:[...Object.entries(e.palette).filter(([,t])=>t.main&&t.light).map(([t])=>({props:{color:t},style:{[`&.${ur.checked}`]:{color:(e.vars||e).palette[t].main,"&:hover":{backgroundColor:e.vars?`rgba(${e.vars.palette[t].mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,Bi.alpha)(e.palette[t].main,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}},[`&.${ur.disabled}`]:{color:e.vars?e.vars.palette.Switch[`${t}DisabledColor`]:`${e.palette.mode==="light"?(0,Bi.lighten)(e.palette[t].main,.62):(0,Bi.darken)(e.palette[t].main,.55)}`}},[`&.${ur.checked} + .${ur.track}`]:{backgroundColor:(e.vars||e).palette[t].main}}}))]})),ZF=M("span",{name:"MuiSwitch",slot:"Track",overridesResolver:(e,t)=>t.track})(({theme:e})=>({height:"100%",width:"100%",borderRadius:14/2,zIndex:-1,transition:e.transitions.create(["opacity","background-color"],{duration:e.transitions.duration.shortest}),backgroundColor:e.vars?e.vars.palette.common.onBackground:`${e.palette.mode==="light"?e.palette.common.black:e.palette.common.white}`,opacity:e.vars?e.vars.opacity.switchTrack:`${e.palette.mode==="light"?.38:.3}`})),JF=M("span",{name:"MuiSwitch",slot:"Thumb",overridesResolver:(e,t)=>t.thumb})(({theme:e})=>({boxShadow:(e.vars||e).shadows[1],backgroundColor:"currentColor",width:20,height:20,borderRadius:"50%"})),e3=gS.forwardRef(function(t,r){let o=Y({props:t,name:"MuiSwitch"}),{className:n,color:s="primary",edge:i=!1,size:a="medium",sx:l}=o,p=k(o,GF),c=d({},o,{color:s,edge:i,size:a}),u=YF(c),f=(0,zm.jsx)(JF,{className:u.thumb,ownerState:c});return(0,vS.jsxs)(XF,{className:A(u.root,n),sx:l,ownerState:c,children:[(0,zm.jsx)(QF,d({type:"checkbox",icon:f,checkedIcon:f,ref:r,ownerState:c},p,{classes:d({},u,{root:u.switchBase})})),(0,zm.jsx)(ZF,{className:u.track,ownerState:c})]})}),yn=e3;J();var Fm=P(L());var xS=P(L()),t3=xS.createContext(),Bm=t3;function TS(e){return K("MuiTable",e)}var Cpe=W("MuiTable",["root","stickyHeader"]);var Yx=P(H()),r3=["className","component","padding","size","stickyHeader"],o3=e=>{let{classes:t,stickyHeader:r}=e;return G({root:["root",r&&"stickyHeader"]},TS,t)},n3=M("table",{name:"MuiTable",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.stickyHeader&&t.stickyHeader]}})(({theme:e,ownerState:t})=>d({display:"table",width:"100%",borderCollapse:"collapse",borderSpacing:0,"& caption":d({},e.typography.body2,{padding:e.spacing(2),color:(e.vars||e).palette.text.secondary,textAlign:"left",captionSide:"bottom"})},t.stickyHeader&&{borderCollapse:"separate"})),bS="table",s3=Fm.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTable"}),{className:n,component:s=bS,padding:i="normal",size:a="medium",stickyHeader:l=!1}=o,p=k(o,r3),c=d({},o,{component:s,padding:i,size:a,stickyHeader:l}),u=o3(c),f=Fm.useMemo(()=>({padding:i,size:a,stickyHeader:l}),[i,a,l]);return(0,Yx.jsx)(Bm.Provider,{value:f,children:(0,Yx.jsx)(n3,d({as:s,role:s===bS?null:"table",ref:r,className:A(u.root,n),ownerState:c},p))})}),_r=s3;J();var wS=P(L());var PS=P(L()),i3=PS.createContext(),Ds=i3;function CS(e){return K("MuiTableBody",e)}var Bpe=W("MuiTableBody",["root"]);var Xx=P(H()),a3=["className","component"],l3=e=>{let{classes:t}=e;return G({root:["root"]},CS,t)},p3=M("tbody",{name:"MuiTableBody",slot:"Root",overridesResolver:(e,t)=>t.root})({display:"table-row-group"}),c3={variant:"body"},$S="tbody",u3=wS.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTableBody"}),{className:n,component:s=$S}=o,i=k(o,a3),a=d({},o,{component:s}),l=l3(a);return(0,Xx.jsx)(Ds.Provider,{value:c3,children:(0,Xx.jsx)(p3,d({className:A(l.root,n),as:s,ref:r,role:s===$S?null:"rowgroup",ownerState:a},i))})}),Rr=u3;J();var Ac=P(L());var Fi=P($r());function _S(e){return K("MuiTableCell",e)}var d3=W("MuiTableCell",["root","head","body","footer","sizeSmall","sizeMedium","paddingCheckbox","paddingNone","alignLeft","alignCenter","alignRight","alignJustify","stickyHeader"]),RS=d3;var ES=P(H()),f3=["align","className","component","padding","scope","size","sortDirection","variant"],m3=e=>{let{classes:t,variant:r,align:o,padding:n,size:s,stickyHeader:i}=e,a={root:["root",r,i&&"stickyHeader",o!=="inherit"&&`align${I(o)}`,n!=="normal"&&`padding${I(n)}`,`size${I(s)}`]};return G(a,_S,t)},y3=M("td",{name:"MuiTableCell",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,t[r.variant],t[`size${I(r.size)}`],r.padding!=="normal"&&t[`padding${I(r.padding)}`],r.align!=="inherit"&&t[`align${I(r.align)}`],r.stickyHeader&&t.stickyHeader]}})(({theme:e,ownerState:t})=>d({},e.typography.body2,{display:"table-cell",verticalAlign:"inherit",borderBottom:e.vars?`1px solid ${e.vars.palette.TableCell.border}`:`1px solid
    ${e.palette.mode==="light"?(0,Fi.lighten)((0,Fi.alpha)(e.palette.divider,1),.88):(0,Fi.darken)((0,Fi.alpha)(e.palette.divider,1),.68)}`,textAlign:"left",padding:16},t.variant==="head"&&{color:(e.vars||e).palette.text.primary,lineHeight:e.typography.pxToRem(24),fontWeight:e.typography.fontWeightMedium},t.variant==="body"&&{color:(e.vars||e).palette.text.primary},t.variant==="footer"&&{color:(e.vars||e).palette.text.secondary,lineHeight:e.typography.pxToRem(21),fontSize:e.typography.pxToRem(12)},t.size==="small"&&{padding:"6px 16px",[`&.${RS.paddingCheckbox}`]:{width:24,padding:"0 12px 0 16px","& > *":{padding:0}}},t.padding==="checkbox"&&{width:48,padding:"0 0 0 4px"},t.padding==="none"&&{padding:0},t.align==="left"&&{textAlign:"left"},t.align==="center"&&{textAlign:"center"},t.align==="right"&&{textAlign:"right",flexDirection:"row-reverse"},t.align==="justify"&&{textAlign:"justify"},t.stickyHeader&&{position:"sticky",top:0,zIndex:2,backgroundColor:(e.vars||e).palette.background.default})),h3=Ac.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTableCell"}),{align:n="inherit",className:s,component:i,padding:a,scope:l,size:p,sortDirection:c,variant:u}=o,f=k(o,f3),v=Ac.useContext(Bm),x=Ac.useContext(Ds),h=x&&x.variant==="head",b;i?b=i:b=h?"th":"td";let y=l;b==="td"?y=void 0:!y&&h&&(y="col");let m=u||x&&x.variant,g=d({},o,{align:n,component:b,padding:a||(v&&v.padding?v.padding:"normal"),size:p||(v&&v.size?v.size:"medium"),sortDirection:c,stickyHeader:m==="head"&&v&&v.stickyHeader,variant:m}),T=m3(g),w=null;return c&&(w=c==="asc"?"ascending":"descending"),(0,ES.jsx)(y3,d({as:b,ref:r,className:A(T.root,s),"aria-sort":w,scope:y,ownerState:g},f))}),X=h3;J();var kS=P(L());function SS(e){return K("MuiTableContainer",e)}var xce=W("MuiTableContainer",["root"]);var OS=P(H()),g3=["className","component"],v3=e=>{let{classes:t}=e;return G({root:["root"]},SS,t)},x3=M("div",{name:"MuiTableContainer",slot:"Root",overridesResolver:(e,t)=>t.root})({width:"100%",overflowX:"auto"}),T3=kS.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTableContainer"}),{className:n,component:s="div"}=o,i=k(o,g3),a=d({},o,{component:s}),l=v3(a);return(0,OS.jsx)(x3,d({ref:r,as:s,className:A(l.root,n),ownerState:a},i))}),Er=T3;J();var IS=P(L());function NS(e){return K("MuiTableHead",e)}var Ice=W("MuiTableHead",["root"]);var Qx=P(H()),b3=["className","component"],P3=e=>{let{classes:t}=e;return G({root:["root"]},NS,t)},C3=M("thead",{name:"MuiTableHead",slot:"Root",overridesResolver:(e,t)=>t.root})({display:"table-header-group"}),$3={variant:"head"},MS="thead",w3=IS.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTableHead"}),{className:n,component:s=MS}=o,i=k(o,b3),a=d({},o,{component:s}),l=P3(a);return(0,Qx.jsx)(Ds.Provider,{value:$3,children:(0,Qx.jsx)(C3,d({as:s,className:A(l.root,n),ref:r,role:s===MS?null:"rowgroup",ownerState:a},i))})}),Sr=w3;J();var Um=P(L());var Jx=P($r());function jS(e){return K("MuiTableRow",e)}var _3=W("MuiTableRow",["root","selected","hover","head","footer"]),Zx=_3;var LS=P(H()),R3=["className","component","hover","selected"],E3=e=>{let{classes:t,selected:r,hover:o,head:n,footer:s}=e;return G({root:["root",r&&"selected",o&&"hover",n&&"head",s&&"footer"]},jS,t)},S3=M("tr",{name:"MuiTableRow",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.head&&t.head,r.footer&&t.footer]}})(({theme:e})=>({color:"inherit",display:"table-row",verticalAlign:"middle",outline:0,[`&.${Zx.hover}:hover`]:{backgroundColor:(e.vars||e).palette.action.hover},[`&.${Zx.selected}`]:{backgroundColor:e.vars?`rgba(${e.vars.palette.primary.mainChannel} / ${e.vars.palette.action.selectedOpacity})`:(0,Jx.alpha)(e.palette.primary.main,e.palette.action.selectedOpacity),"&:hover":{backgroundColor:e.vars?`rgba(${e.vars.palette.primary.mainChannel} / calc(${e.vars.palette.action.selectedOpacity} + ${e.vars.palette.action.hoverOpacity}))`:(0,Jx.alpha)(e.palette.primary.main,e.palette.action.selectedOpacity+e.palette.action.hoverOpacity)}}})),DS="tr",k3=Um.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTableRow"}),{className:n,component:s=DS,hover:i=!1,selected:a=!1}=o,l=k(o,R3),p=Um.useContext(Ds),c=d({},o,{component:s,hover:i,selected:a,head:p&&p.variant==="head",footer:p&&p.variant==="footer"}),u=E3(c);return(0,LS.jsx)(S3,d({as:s,ref:r,className:A(u.root,n),role:s===DS?null:"row",ownerState:c},l))}),nt=k3;J();var zk=P(L());J();var VS=P(L());var HS=P(Wt());J();var US=P(ni()),dr=P(L());J();var ko=P(L());var eT=P(H()),AS=P(H()),O3=["onChange","maxRows","minRows","style","value"];function Wm(e){return parseInt(e,10)||0}var N3={shadow:{visibility:"hidden",position:"absolute",overflow:"hidden",height:0,top:0,left:0,transform:"translateZ(0)"}};function M3(e){return e==null||Object.keys(e).length===0||e.outerHeightStyle===0&&!e.overflowing}var I3=ko.forwardRef(function(t,r){let{onChange:o,maxRows:n,minRows:s=1,style:i,value:a}=t,l=k(t,O3),{current:p}=ko.useRef(a!=null),c=ko.useRef(null),u=yt(r,c),f=ko.useRef(null),v=ko.useRef(null),x=ko.useCallback(()=>{let y=c.current,g=xo(y).getComputedStyle(y);if(g.width==="0px")return{outerHeightStyle:0,overflowing:!1};let T=v.current;T.style.width=g.width,T.value=y.value||t.placeholder||"x",T.value.slice(-1)===`
`&&(T.value+=" ");let w=g.boxSizing,$=Wm(g.paddingBottom)+Wm(g.paddingTop),C=Wm(g.borderBottomWidth)+Wm(g.borderTopWidth),_=T.scrollHeight;T.value="x";let S=T.scrollHeight,R=_;s&&(R=Math.max(Number(s)*S,R)),n&&(R=Math.min(Number(n)*S,R)),R=Math.max(R,S);let j=R+(w==="border-box"?$+C:0),U=Math.abs(R-_)<=1;return{outerHeightStyle:j,overflowing:U}},[n,s,t.placeholder]),h=ko.useCallback(()=>{let y=x();if(M3(y))return;let m=y.outerHeightStyle,g=c.current;f.current!==m&&(f.current=m,g.style.height=`${m}px`),g.style.overflow=y.overflowing?"hidden":""},[x]);return Nt(()=>{let y=()=>{h()},m,g=()=>{cancelAnimationFrame(m),m=requestAnimationFrame(()=>{y()})},T=vi(y),w=c.current,$=xo(w);$.addEventListener("resize",T);let C;return typeof ResizeObserver<"u"&&(C=new ResizeObserver(y),C.observe(w)),()=>{T.clear(),cancelAnimationFrame(m),$.removeEventListener("resize",T),C&&C.disconnect()}},[x,h]),Nt(()=>{h()}),(0,AS.jsxs)(ko.Fragment,{children:[(0,eT.jsx)("textarea",d({value:a,onChange:y=>{p||h(),o&&o(y)},ref:u,rows:s,style:i},l)),(0,eT.jsx)("textarea",{"aria-hidden":!0,className:t.className,readOnly:!0,ref:v,tabIndex:-1,style:d({},N3.shadow,i,{paddingTop:0,paddingBottom:0})})]})}),tT=I3;function no({props:e,states:t,muiFormControl:r}){return t.reduce((o,n)=>(o[n]=e[n],r&&typeof e[n]>"u"&&(o[n]=r[n]),o),{})}function zS(e){return e!=null&&!(Array.isArray(e)&&e.length===0)}function Ui(e,t=!1){return e&&(zS(e.value)&&e.value!==""||t&&zS(e.defaultValue)&&e.defaultValue!=="")}function BS(e){return e.startAdornment}function FS(e){return K("MuiInputBase",e)}var j3=W("MuiInputBase",["root","formControl","focused","disabled","adornedStart","adornedEnd","error","sizeSmall","multiline","colorSecondary","fullWidth","hiddenLabel","readOnly","input","inputSizeSmall","inputMultiline","inputTypeSearch","inputAdornedStart","inputAdornedEnd","inputHiddenLabel"]),Qo=j3;var Vm=P(H()),rT=P(H()),D3=["aria-describedby","autoComplete","autoFocus","className","color","components","componentsProps","defaultValue","disabled","disableInjectingGlobalStyles","endAdornment","error","fullWidth","id","inputComponent","inputProps","inputRef","margin","maxRows","minRows","multiline","name","onBlur","onChange","onClick","onFocus","onKeyDown","onKeyUp","placeholder","readOnly","renderSuffix","rows","size","slotProps","slots","startAdornment","type","value"],Wi=(e,t)=>{let{ownerState:r}=e;return[t.root,r.formControl&&t.formControl,r.startAdornment&&t.adornedStart,r.endAdornment&&t.adornedEnd,r.error&&t.error,r.size==="small"&&t.sizeSmall,r.multiline&&t.multiline,r.color&&t[`color${I(r.color)}`],r.fullWidth&&t.fullWidth,r.hiddenLabel&&t.hiddenLabel]},Vi=(e,t)=>{let{ownerState:r}=e;return[t.input,r.size==="small"&&t.inputSizeSmall,r.multiline&&t.inputMultiline,r.type==="search"&&t.inputTypeSearch,r.startAdornment&&t.inputAdornedStart,r.endAdornment&&t.inputAdornedEnd,r.hiddenLabel&&t.inputHiddenLabel]},L3=e=>{let{classes:t,color:r,disabled:o,error:n,endAdornment:s,focused:i,formControl:a,fullWidth:l,hiddenLabel:p,multiline:c,readOnly:u,size:f,startAdornment:v,type:x}=e,h={root:["root",`color${I(r)}`,o&&"disabled",n&&"error",l&&"fullWidth",i&&"focused",a&&"formControl",f&&f!=="medium"&&`size${I(f)}`,c&&"multiline",v&&"adornedStart",s&&"adornedEnd",p&&"hiddenLabel",u&&"readOnly"],input:["input",o&&"disabled",x==="search"&&"inputTypeSearch",c&&"inputMultiline",f==="small"&&"inputSizeSmall",p&&"inputHiddenLabel",v&&"inputAdornedStart",s&&"inputAdornedEnd",u&&"readOnly"]};return G(h,FS,t)},Hi=M("div",{name:"MuiInputBase",slot:"Root",overridesResolver:Wi})(({theme:e,ownerState:t})=>d({},e.typography.body1,{color:(e.vars||e).palette.text.primary,lineHeight:"1.4375em",boxSizing:"border-box",position:"relative",cursor:"text",display:"inline-flex",alignItems:"center",[`&.${Qo.disabled}`]:{color:(e.vars||e).palette.text.disabled,cursor:"default"}},t.multiline&&d({padding:"4px 0 5px"},t.size==="small"&&{paddingTop:1}),t.fullWidth&&{width:"100%"})),qi=M("input",{name:"MuiInputBase",slot:"Input",overridesResolver:Vi})(({theme:e,ownerState:t})=>{let r=e.palette.mode==="light",o=d({color:"currentColor"},e.vars?{opacity:e.vars.opacity.inputPlaceholder}:{opacity:r?.42:.5},{transition:e.transitions.create("opacity",{duration:e.transitions.duration.shorter})}),n={opacity:"0 !important"},s=e.vars?{opacity:e.vars.opacity.inputPlaceholder}:{opacity:r?.42:.5};return d({font:"inherit",letterSpacing:"inherit",color:"currentColor",padding:"4px 0 5px",border:0,boxSizing:"content-box",background:"none",height:"1.4375em",margin:0,WebkitTapHighlightColor:"transparent",display:"block",minWidth:0,width:"100%",animationName:"mui-auto-fill-cancel",animationDuration:"10ms","&::-webkit-input-placeholder":o,"&::-moz-placeholder":o,"&:-ms-input-placeholder":o,"&::-ms-input-placeholder":o,"&:focus":{outline:0},"&:invalid":{boxShadow:"none"},"&::-webkit-search-decoration":{WebkitAppearance:"none"},[`label[data-shrink=false] + .${Qo.formControl} &`]:{"&::-webkit-input-placeholder":n,"&::-moz-placeholder":n,"&:-ms-input-placeholder":n,"&::-ms-input-placeholder":n,"&:focus::-webkit-input-placeholder":s,"&:focus::-moz-placeholder":s,"&:focus:-ms-input-placeholder":s,"&:focus::-ms-input-placeholder":s},[`&.${Qo.disabled}`]:{opacity:1,WebkitTextFillColor:(e.vars||e).palette.text.disabled},"&:-webkit-autofill":{animationDuration:"5000s",animationName:"mui-auto-fill"}},t.size==="small"&&{paddingTop:1},t.multiline&&{height:"auto",resize:"none",padding:0,paddingTop:0},t.type==="search"&&{MozAppearance:"textfield"})}),A3=(0,Vm.jsx)(Oc,{styles:{"@keyframes mui-auto-fill":{from:{display:"block"}},"@keyframes mui-auto-fill-cancel":{from:{display:"block"}}}}),z3=dr.forwardRef(function(t,r){var o;let n=Y({props:t,name:"MuiInputBase"}),{"aria-describedby":s,autoComplete:i,autoFocus:a,className:l,components:p={},componentsProps:c={},defaultValue:u,disabled:f,disableInjectingGlobalStyles:v,endAdornment:x,fullWidth:h=!1,id:b,inputComponent:y="input",inputProps:m={},inputRef:g,maxRows:T,minRows:w,multiline:$=!1,name:C,onBlur:_,onChange:S,onClick:R,onFocus:j,onKeyDown:U,onKeyUp:z,placeholder:Z,readOnly:B,renderSuffix:D,rows:q,slotProps:E={},slots:F={},startAdornment:ae,type:ye="text",value:me}=n,te=k(n,D3),ne=m.value!=null?m.value:me,{current:ue}=dr.useRef(ne!=null),he=dr.useRef(),be=dr.useCallback(Se=>{},[]),Te=Qe(he,g,m.ref,be),[Pe,Ke]=dr.useState(!1),N=wr(),V=no({props:n,muiFormControl:N,states:["color","disabled","error","hiddenLabel","size","required","filled"]});V.focused=N?N.focused:Pe,dr.useEffect(()=>{!N&&f&&Pe&&(Ke(!1),_&&_())},[N,f,Pe,_]);let re=N&&N.onFilled,de=N&&N.onEmpty,ge=dr.useCallback(Se=>{Ui(Se)?re&&re():de&&de()},[re,de]);Sl(()=>{ue&&ge({value:ne})},[ne,ge,ue]);let yr=Se=>{if(V.disabled){Se.stopPropagation();return}j&&j(Se),m.onFocus&&m.onFocus(Se),N&&N.onFocus?N.onFocus(Se):Ke(!0)},Kt=Se=>{_&&_(Se),m.onBlur&&m.onBlur(Se),N&&N.onBlur?N.onBlur(Se):Ke(!1)},wt=(Se,...ce)=>{if(!ue){let _t=Se.target||he.current;if(_t==null)throw new Error((0,US.default)(1));ge({value:_t.value})}m.onChange&&m.onChange(Se,...ce),S&&S(Se,...ce)};dr.useEffect(()=>{ge(he.current)},[]);let or=Se=>{he.current&&Se.currentTarget===Se.target&&he.current.focus(),R&&R(Se)},Je=y,Ie=m;$&&Je==="input"&&(q?Ie=d({type:void 0,minRows:q,maxRows:q},Ie):Ie=d({type:void 0,maxRows:T,minRows:w},Ie),Je=tT);let Gt=Se=>{ge(Se.animationName==="mui-auto-fill-cancel"?he.current:{value:"x"})};dr.useEffect(()=>{N&&N.setAdornedStart(!!ae)},[N,ae]);let vt=d({},n,{color:V.color||"primary",disabled:V.disabled,endAdornment:x,error:V.error,focused:V.focused,formControl:N,fullWidth:h,hiddenLabel:V.hiddenLabel,multiline:$,size:V.size,startAdornment:ae,type:ye}),Oe=L3(vt),Yt=F.root||p.Root||Hi,hr=E.root||c.root||{},Or=F.input||p.Input||qi;return Ie=d({},Ie,(o=E.input)!=null?o:c.input),(0,rT.jsxs)(dr.Fragment,{children:[!v&&A3,(0,rT.jsxs)(Yt,d({},hr,!ws(Yt)&&{ownerState:d({},vt,hr.ownerState)},{ref:r,onClick:or},te,{className:A(Oe.root,hr.className,l,B&&"MuiInputBase-readOnly"),children:[ae,(0,Vm.jsx)(Pl.Provider,{value:null,children:(0,Vm.jsx)(Or,d({ownerState:vt,"aria-invalid":V.error,"aria-describedby":s,autoComplete:i,autoFocus:a,defaultValue:u,disabled:V.disabled,id:b,onAnimationStart:Gt,name:C,placeholder:Z,readOnly:B,required:V.required,rows:q,value:ne,onKeyDown:U,onKeyUp:z,type:ye},Ie,!ws(Or)&&{as:Je,ownerState:d({},vt,Ie.ownerState)},{ref:Te,className:A(Oe.input,Ie.className,B&&"MuiInputBase-readOnly"),onBlur:Kt,onChange:wt,onFocus:yr}))}),x,D?D(d({},V,{startAdornment:ae})):null]}))]})}),Ki=z3;J();function WS(e){return K("MuiInput",e)}var B3=d({},Qo,W("MuiInput",["root","underline","input"])),Dl=B3;var qS=P(H()),F3=["disableUnderline","components","componentsProps","fullWidth","inputComponent","multiline","slotProps","slots","type"],U3=e=>{let{classes:t,disableUnderline:r}=e,n=G({root:["root",!r&&"underline"],input:["input"]},WS,t);return d({},t,n)},W3=M(Hi,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiInput",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[...Wi(e,t),!r.disableUnderline&&t.underline]}})(({theme:e,ownerState:t})=>{let o=e.palette.mode==="light"?"rgba(0, 0, 0, 0.42)":"rgba(255, 255, 255, 0.7)";return e.vars&&(o=`rgba(${e.vars.palette.common.onBackgroundChannel} / ${e.vars.opacity.inputUnderline})`),d({position:"relative"},t.formControl&&{"label + &":{marginTop:16}},!t.disableUnderline&&{"&::after":{borderBottom:`2px solid ${(e.vars||e).palette[t.color].main}`,left:0,bottom:0,content:'""',position:"absolute",right:0,transform:"scaleX(0)",transition:e.transitions.create("transform",{duration:e.transitions.duration.shorter,easing:e.transitions.easing.easeOut}),pointerEvents:"none"},[`&.${Dl.focused}:after`]:{transform:"scaleX(1) translateX(0)"},[`&.${Dl.error}`]:{"&::before, &::after":{borderBottomColor:(e.vars||e).palette.error.main}},"&::before":{borderBottom:`1px solid ${o}`,left:0,bottom:0,content:'"\\00a0"',position:"absolute",right:0,transition:e.transitions.create("border-bottom-color",{duration:e.transitions.duration.shorter}),pointerEvents:"none"},[`&:hover:not(.${Dl.disabled}, .${Dl.error}):before`]:{borderBottom:`2px solid ${(e.vars||e).palette.text.primary}`,"@media (hover: none)":{borderBottom:`1px solid ${o}`}},[`&.${Dl.disabled}:before`]:{borderBottomStyle:"dotted"}})}),V3=M(qi,{name:"MuiInput",slot:"Input",overridesResolver:Vi})({}),KS=VS.forwardRef(function(t,r){var o,n,s,i;let a=Y({props:t,name:"MuiInput"}),{disableUnderline:l,components:p={},componentsProps:c,fullWidth:u=!1,inputComponent:f="input",multiline:v=!1,slotProps:x,slots:h={},type:b="text"}=a,y=k(a,F3),m=U3(a),T={root:{ownerState:{disableUnderline:l}}},w=x??c?(0,HS.default)(x??c,T):T,$=(o=(n=h.root)!=null?n:p.Root)!=null?o:W3,C=(s=(i=h.input)!=null?i:p.Input)!=null?s:V3;return(0,qS.jsx)(Ki,d({slots:{root:$,input:C},slotProps:w,fullWidth:u,inputComponent:f,multiline:v,ref:r,type:b},y,{classes:m}))});KS.muiName="Input";var zc=KS;J();var YS=P(L()),XS=P(Wt());J();function GS(e){return K("MuiFilledInput",e)}var H3=d({},Qo,W("MuiFilledInput",["root","underline","input"])),Ls=H3;var QS=P(H()),q3=["disableUnderline","components","componentsProps","fullWidth","hiddenLabel","inputComponent","multiline","slotProps","slots","type"],K3=e=>{let{classes:t,disableUnderline:r}=e,n=G({root:["root",!r&&"underline"],input:["input"]},GS,t);return d({},t,n)},G3=M(Hi,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiFilledInput",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[...Wi(e,t),!r.disableUnderline&&t.underline]}})(({theme:e,ownerState:t})=>{var r;let o=e.palette.mode==="light",n=o?"rgba(0, 0, 0, 0.42)":"rgba(255, 255, 255, 0.7)",s=o?"rgba(0, 0, 0, 0.06)":"rgba(255, 255, 255, 0.09)",i=o?"rgba(0, 0, 0, 0.09)":"rgba(255, 255, 255, 0.13)",a=o?"rgba(0, 0, 0, 0.12)":"rgba(255, 255, 255, 0.12)";return d({position:"relative",backgroundColor:e.vars?e.vars.palette.FilledInput.bg:s,borderTopLeftRadius:(e.vars||e).shape.borderRadius,borderTopRightRadius:(e.vars||e).shape.borderRadius,transition:e.transitions.create("background-color",{duration:e.transitions.duration.shorter,easing:e.transitions.easing.easeOut}),"&:hover":{backgroundColor:e.vars?e.vars.palette.FilledInput.hoverBg:i,"@media (hover: none)":{backgroundColor:e.vars?e.vars.palette.FilledInput.bg:s}},[`&.${Ls.focused}`]:{backgroundColor:e.vars?e.vars.palette.FilledInput.bg:s},[`&.${Ls.disabled}`]:{backgroundColor:e.vars?e.vars.palette.FilledInput.disabledBg:a}},!t.disableUnderline&&{"&::after":{borderBottom:`2px solid ${(r=(e.vars||e).palette[t.color||"primary"])==null?void 0:r.main}`,left:0,bottom:0,content:'""',position:"absolute",right:0,transform:"scaleX(0)",transition:e.transitions.create("transform",{duration:e.transitions.duration.shorter,easing:e.transitions.easing.easeOut}),pointerEvents:"none"},[`&.${Ls.focused}:after`]:{transform:"scaleX(1) translateX(0)"},[`&.${Ls.error}`]:{"&::before, &::after":{borderBottomColor:(e.vars||e).palette.error.main}},"&::before":{borderBottom:`1px solid ${e.vars?`rgba(${e.vars.palette.common.onBackgroundChannel} / ${e.vars.opacity.inputUnderline})`:n}`,left:0,bottom:0,content:'"\\00a0"',position:"absolute",right:0,transition:e.transitions.create("border-bottom-color",{duration:e.transitions.duration.shorter}),pointerEvents:"none"},[`&:hover:not(.${Ls.disabled}, .${Ls.error}):before`]:{borderBottom:`1px solid ${(e.vars||e).palette.text.primary}`},[`&.${Ls.disabled}:before`]:{borderBottomStyle:"dotted"}},t.startAdornment&&{paddingLeft:12},t.endAdornment&&{paddingRight:12},t.multiline&&d({padding:"25px 12px 8px"},t.size==="small"&&{paddingTop:21,paddingBottom:4},t.hiddenLabel&&{paddingTop:16,paddingBottom:17},t.hiddenLabel&&t.size==="small"&&{paddingTop:8,paddingBottom:9}))}),Y3=M(qi,{name:"MuiFilledInput",slot:"Input",overridesResolver:Vi})(({theme:e,ownerState:t})=>d({paddingTop:25,paddingRight:12,paddingBottom:8,paddingLeft:12},!e.vars&&{"&:-webkit-autofill":{WebkitBoxShadow:e.palette.mode==="light"?null:"0 0 0 100px #266798 inset",WebkitTextFillColor:e.palette.mode==="light"?null:"#fff",caretColor:e.palette.mode==="light"?null:"#fff",borderTopLeftRadius:"inherit",borderTopRightRadius:"inherit"}},e.vars&&{"&:-webkit-autofill":{borderTopLeftRadius:"inherit",borderTopRightRadius:"inherit"},[e.getColorSchemeSelector("dark")]:{"&:-webkit-autofill":{WebkitBoxShadow:"0 0 0 100px #266798 inset",WebkitTextFillColor:"#fff",caretColor:"#fff"}}},t.size==="small"&&{paddingTop:21,paddingBottom:4},t.hiddenLabel&&{paddingTop:16,paddingBottom:17},t.startAdornment&&{paddingLeft:0},t.endAdornment&&{paddingRight:0},t.hiddenLabel&&t.size==="small"&&{paddingTop:8,paddingBottom:9},t.multiline&&{paddingTop:0,paddingBottom:0,paddingLeft:0,paddingRight:0})),ZS=YS.forwardRef(function(t,r){var o,n,s,i;let a=Y({props:t,name:"MuiFilledInput"}),{components:l={},componentsProps:p,fullWidth:c=!1,inputComponent:u="input",multiline:f=!1,slotProps:v,slots:x={},type:h="text"}=a,b=k(a,q3),y=d({},a,{fullWidth:c,inputComponent:u,multiline:f,type:h}),m=K3(a),g={root:{ownerState:y},input:{ownerState:y}},T=v??p?(0,XS.default)(g,v??p):g,w=(o=(n=x.root)!=null?n:l.Root)!=null?o:G3,$=(s=(i=x.input)!=null?i:l.Input)!=null?s:Y3;return(0,QS.jsx)(Ki,d({slots:{root:w,input:$},componentsProps:T,fullWidth:c,inputComponent:u,multiline:f,ref:r,type:h},b,{classes:m}))});ZS.muiName="Input";var Bc=ZS;J();var Hm=P(L());J();var $de=P(L());var Fc=P(H()),JS,X3=["children","classes","className","label","notched"],Q3=M("fieldset",{shouldForwardProp:je})({textAlign:"left",position:"absolute",bottom:0,right:0,top:-5,left:0,margin:0,padding:"0 8px",pointerEvents:"none",borderRadius:"inherit",borderStyle:"solid",borderWidth:1,overflow:"hidden",minWidth:"0%"}),Z3=M("legend",{shouldForwardProp:je})(({ownerState:e,theme:t})=>d({float:"unset",width:"auto",overflow:"hidden"},!e.withLabel&&{padding:0,lineHeight:"11px",transition:t.transitions.create("width",{duration:150,easing:t.transitions.easing.easeOut})},e.withLabel&&d({display:"block",padding:0,height:11,fontSize:"0.75em",visibility:"hidden",maxWidth:.01,transition:t.transitions.create("max-width",{duration:50,easing:t.transitions.easing.easeOut}),whiteSpace:"nowrap","& > span":{paddingLeft:5,paddingRight:5,display:"inline-block",opacity:0,visibility:"visible"}},e.notched&&{maxWidth:"100%",transition:t.transitions.create("max-width",{duration:100,easing:t.transitions.easing.easeOut,delay:50})})));function oT(e){let{className:t,label:r,notched:o}=e,n=k(e,X3),s=r!=null&&r!=="",i=d({},e,{notched:o,withLabel:s});return(0,Fc.jsx)(Q3,d({"aria-hidden":!0,className:t,ownerState:i},n,{children:(0,Fc.jsx)(Z3,{ownerState:i,children:s?(0,Fc.jsx)("span",{children:r}):JS||(JS=(0,Fc.jsx)("span",{className:"notranslate",children:"\u200B"}))})}))}J();function ek(e){return K("MuiOutlinedInput",e)}var J3=d({},Qo,W("MuiOutlinedInput",["root","notchedOutline","input"])),Vn=J3;var tk=P(H()),nT=P(H()),eU=["components","fullWidth","inputComponent","label","multiline","notched","slots","type"],tU=e=>{let{classes:t}=e,o=G({root:["root"],notchedOutline:["notchedOutline"],input:["input"]},ek,t);return d({},t,o)},rU=M(Hi,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiOutlinedInput",slot:"Root",overridesResolver:Wi})(({theme:e,ownerState:t})=>{let r=e.palette.mode==="light"?"rgba(0, 0, 0, 0.23)":"rgba(255, 255, 255, 0.23)";return d({position:"relative",borderRadius:(e.vars||e).shape.borderRadius,[`&:hover .${Vn.notchedOutline}`]:{borderColor:(e.vars||e).palette.text.primary},"@media (hover: none)":{[`&:hover .${Vn.notchedOutline}`]:{borderColor:e.vars?`rgba(${e.vars.palette.common.onBackgroundChannel} / 0.23)`:r}},[`&.${Vn.focused} .${Vn.notchedOutline}`]:{borderColor:(e.vars||e).palette[t.color].main,borderWidth:2},[`&.${Vn.error} .${Vn.notchedOutline}`]:{borderColor:(e.vars||e).palette.error.main},[`&.${Vn.disabled} .${Vn.notchedOutline}`]:{borderColor:(e.vars||e).palette.action.disabled}},t.startAdornment&&{paddingLeft:14},t.endAdornment&&{paddingRight:14},t.multiline&&d({padding:"16.5px 14px"},t.size==="small"&&{padding:"8.5px 14px"}))}),oU=M(oT,{name:"MuiOutlinedInput",slot:"NotchedOutline",overridesResolver:(e,t)=>t.notchedOutline})(({theme:e})=>{let t=e.palette.mode==="light"?"rgba(0, 0, 0, 0.23)":"rgba(255, 255, 255, 0.23)";return{borderColor:e.vars?`rgba(${e.vars.palette.common.onBackgroundChannel} / 0.23)`:t}}),nU=M(qi,{name:"MuiOutlinedInput",slot:"Input",overridesResolver:Vi})(({theme:e,ownerState:t})=>d({padding:"16.5px 14px"},!e.vars&&{"&:-webkit-autofill":{WebkitBoxShadow:e.palette.mode==="light"?null:"0 0 0 100px #266798 inset",WebkitTextFillColor:e.palette.mode==="light"?null:"#fff",caretColor:e.palette.mode==="light"?null:"#fff",borderRadius:"inherit"}},e.vars&&{"&:-webkit-autofill":{borderRadius:"inherit"},[e.getColorSchemeSelector("dark")]:{"&:-webkit-autofill":{WebkitBoxShadow:"0 0 0 100px #266798 inset",WebkitTextFillColor:"#fff",caretColor:"#fff"}}},t.size==="small"&&{padding:"8.5px 14px"},t.multiline&&{padding:0},t.startAdornment&&{paddingLeft:0},t.endAdornment&&{paddingRight:0})),rk=Hm.forwardRef(function(t,r){var o,n,s,i,a;let l=Y({props:t,name:"MuiOutlinedInput"}),{components:p={},fullWidth:c=!1,inputComponent:u="input",label:f,multiline:v=!1,notched:x,slots:h={},type:b="text"}=l,y=k(l,eU),m=tU(l),g=wr(),T=no({props:l,muiFormControl:g,states:["color","disabled","error","focused","hiddenLabel","size","required"]}),w=d({},l,{color:T.color||"primary",disabled:T.disabled,error:T.error,focused:T.focused,formControl:g,fullWidth:c,hiddenLabel:T.hiddenLabel,multiline:v,size:T.size,type:b}),$=(o=(n=h.root)!=null?n:p.Root)!=null?o:rU,C=(s=(i=h.input)!=null?i:p.Input)!=null?s:nU;return(0,nT.jsx)(Ki,d({slots:{root:$,input:C},renderSuffix:_=>(0,nT.jsx)(oU,{ownerState:w,className:m.notchedOutline,label:f!=null&&f!==""&&T.required?a||(a=(0,tk.jsxs)(Hm.Fragment,{children:[f,"\u2009","*"]})):f,notched:typeof x<"u"?x:!!(_.startAdornment||_.filled||_.focused)}),fullWidth:c,inputComponent:u,multiline:v,ref:r,type:b},y,{classes:d({},m,{notchedOutline:null})}))});rk.muiName="Input";var Uc=rk;J();var ik=P(L());J();var nk=P(L());function ok(e){return K("MuiFormLabel",e)}var sU=W("MuiFormLabel",["root","colorSecondary","focused","disabled","error","filled","required","asterisk"]),As=sU;var sT=P(H()),iU=["children","className","color","component","disabled","error","filled","focused","required"],aU=e=>{let{classes:t,color:r,focused:o,disabled:n,error:s,filled:i,required:a}=e,l={root:["root",`color${I(r)}`,n&&"disabled",s&&"error",i&&"filled",o&&"focused",a&&"required"],asterisk:["asterisk",s&&"error"]};return G(l,ok,t)},lU=M("label",{name:"MuiFormLabel",slot:"Root",overridesResolver:({ownerState:e},t)=>d({},t.root,e.color==="secondary"&&t.colorSecondary,e.filled&&t.filled)})(({theme:e,ownerState:t})=>d({color:(e.vars||e).palette.text.secondary},e.typography.body1,{lineHeight:"1.4375em",padding:0,position:"relative",[`&.${As.focused}`]:{color:(e.vars||e).palette[t.color].main},[`&.${As.disabled}`]:{color:(e.vars||e).palette.text.disabled},[`&.${As.error}`]:{color:(e.vars||e).palette.error.main}})),pU=M("span",{name:"MuiFormLabel",slot:"Asterisk",overridesResolver:(e,t)=>t.asterisk})(({theme:e})=>({[`&.${As.error}`]:{color:(e.vars||e).palette.error.main}})),cU=nk.forwardRef(function(t,r){let o=Y({props:t,name:"MuiFormLabel"}),{children:n,className:s,component:i="label"}=o,a=k(o,iU),l=wr(),p=no({props:o,muiFormControl:l,states:["color","required","focused","disabled","error","filled"]}),c=d({},o,{color:p.color||"primary",component:i,disabled:p.disabled,error:p.error,filled:p.filled,focused:p.focused,required:p.required}),u=aU(c);return(0,sT.jsxs)(lU,d({as:i,ownerState:c,className:A(u.root,s),ref:r},a,{children:[n,p.required&&(0,sT.jsxs)(pU,{ownerState:c,"aria-hidden":!0,className:u.asterisk,children:["\u2009","*"]})]}))}),iT=cU;function sk(e){return K("MuiInputLabel",e)}var ffe=W("MuiInputLabel",["root","focused","disabled","error","required","asterisk","formControl","sizeSmall","shrink","animated","standard","filled","outlined"]);var ak=P(H()),uU=["disableAnimation","margin","shrink","variant","className"],dU=e=>{let{classes:t,formControl:r,size:o,shrink:n,disableAnimation:s,variant:i,required:a}=e,l={root:["root",r&&"formControl",!s&&"animated",n&&"shrink",o&&o!=="normal"&&`size${I(o)}`,i],asterisk:[a&&"asterisk"]},p=G(l,sk,t);return d({},t,p)},fU=M(iT,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiInputLabel",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[{[`& .${As.asterisk}`]:t.asterisk},t.root,r.formControl&&t.formControl,r.size==="small"&&t.sizeSmall,r.shrink&&t.shrink,!r.disableAnimation&&t.animated,r.focused&&t.focused,t[r.variant]]}})(({theme:e,ownerState:t})=>d({display:"block",transformOrigin:"top left",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis",maxWidth:"100%"},t.formControl&&{position:"absolute",left:0,top:0,transform:"translate(0, 20px) scale(1)"},t.size==="small"&&{transform:"translate(0, 17px) scale(1)"},t.shrink&&{transform:"translate(0, -1.5px) scale(0.75)",transformOrigin:"top left",maxWidth:"133%"},!t.disableAnimation&&{transition:e.transitions.create(["color","transform","max-width"],{duration:e.transitions.duration.shorter,easing:e.transitions.easing.easeOut})},t.variant==="filled"&&d({zIndex:1,pointerEvents:"none",transform:"translate(12px, 16px) scale(1)",maxWidth:"calc(100% - 24px)"},t.size==="small"&&{transform:"translate(12px, 13px) scale(1)"},t.shrink&&d({userSelect:"none",pointerEvents:"auto",transform:"translate(12px, 7px) scale(0.75)",maxWidth:"calc(133% - 24px)"},t.size==="small"&&{transform:"translate(12px, 4px) scale(0.75)"})),t.variant==="outlined"&&d({zIndex:1,pointerEvents:"none",transform:"translate(14px, 16px) scale(1)",maxWidth:"calc(100% - 24px)"},t.size==="small"&&{transform:"translate(14px, 9px) scale(1)"},t.shrink&&{userSelect:"none",pointerEvents:"auto",maxWidth:"calc(133% - 32px)",transform:"translate(14px, -9px) scale(0.75)"}))),mU=ik.forwardRef(function(t,r){let o=Y({name:"MuiInputLabel",props:t}),{disableAnimation:n=!1,shrink:s,className:i}=o,a=k(o,uU),l=wr(),p=s;typeof p>"u"&&l&&(p=l.filled||l.focused||l.adornedStart);let c=no({props:o,muiFormControl:l,states:["size","variant","required","focused"]}),u=d({},o,{disableAnimation:n,formControl:l,shrink:p,size:c.size,variant:c.variant,required:c.required,focused:c.focused}),f=dU(u);return(0,ak.jsx)(fU,d({"data-shrink":p,ownerState:u,ref:r,className:A(f.root,i)},a,{classes:f}))}),aT=mU;J();var Oo=P(L());function lk(e){return K("MuiFormControl",e)}var Nfe=W("MuiFormControl",["root","marginNone","marginNormal","marginDense","fullWidth","disabled"]);var lT=P(H()),yU=["children","className","color","component","disabled","error","focused","fullWidth","hiddenLabel","margin","required","size","variant"],hU=e=>{let{classes:t,margin:r,fullWidth:o}=e,n={root:["root",r!=="none"&&`margin${I(r)}`,o&&"fullWidth"]};return G(n,lk,t)},gU=M("div",{name:"MuiFormControl",slot:"Root",overridesResolver:({ownerState:e},t)=>d({},t.root,t[`margin${I(e.margin)}`],e.fullWidth&&t.fullWidth)})(({ownerState:e})=>d({display:"inline-flex",flexDirection:"column",position:"relative",minWidth:0,padding:0,margin:0,border:0,verticalAlign:"top"},e.margin==="normal"&&{marginTop:16,marginBottom:8},e.margin==="dense"&&{marginTop:8,marginBottom:4},e.fullWidth&&{width:"100%"})),vU=Oo.forwardRef(function(t,r){let o=Y({props:t,name:"MuiFormControl"}),{children:n,className:s,color:i="primary",component:a="div",disabled:l=!1,error:p=!1,focused:c,fullWidth:u=!1,hiddenLabel:f=!1,margin:v="none",required:x=!1,size:h="medium",variant:b="outlined"}=o,y=k(o,yU),m=d({},o,{color:i,component:a,disabled:l,error:p,fullWidth:u,hiddenLabel:f,margin:v,required:x,size:h,variant:b}),g=hU(m),[T,w]=Oo.useState(()=>{let z=!1;return n&&Oo.Children.forEach(n,Z=>{if(!km(Z,["Input","Select"]))return;let B=km(Z,["Select"])?Z.props.input:Z;B&&BS(B.props)&&(z=!0)}),z}),[$,C]=Oo.useState(()=>{let z=!1;return n&&Oo.Children.forEach(n,Z=>{km(Z,["Input","Select"])&&(Ui(Z.props,!0)||Ui(Z.props.inputProps,!0))&&(z=!0)}),z}),[_,S]=Oo.useState(!1);l&&_&&S(!1);let R=c!==void 0&&!l?c:_,j,U=Oo.useMemo(()=>({adornedStart:T,setAdornedStart:w,color:i,disabled:l,error:p,filled:$,focused:R,fullWidth:u,hiddenLabel:f,size:h,onBlur:()=>{S(!1)},onEmpty:()=>{C(!1)},onFilled:()=>{C(!0)},onFocus:()=>{S(!0)},registerEffect:j,required:x,variant:b}),[T,i,l,p,$,R,u,f,j,x,h,b]);return(0,lT.jsx)(Pl.Provider,{value:U,children:(0,lT.jsx)(gU,d({as:a,ownerState:m,className:A(g.root,s),ref:r},y,{children:n}))})}),pT=vU;J();var uk=P(L());function pk(e){return K("MuiFormHelperText",e)}var xU=W("MuiFormHelperText",["root","error","disabled","sizeSmall","sizeMedium","contained","focused","filled","required"]),cT=xU;var uT=P(H()),ck,TU=["children","className","component","disabled","error","filled","focused","margin","required","variant"],bU=e=>{let{classes:t,contained:r,size:o,disabled:n,error:s,filled:i,focused:a,required:l}=e,p={root:["root",n&&"disabled",s&&"error",o&&`size${I(o)}`,r&&"contained",a&&"focused",i&&"filled",l&&"required"]};return G(p,pk,t)},PU=M("p",{name:"MuiFormHelperText",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,r.size&&t[`size${I(r.size)}`],r.contained&&t.contained,r.filled&&t.filled]}})(({theme:e,ownerState:t})=>d({color:(e.vars||e).palette.text.secondary},e.typography.caption,{textAlign:"left",marginTop:3,marginRight:0,marginBottom:0,marginLeft:0,[`&.${cT.disabled}`]:{color:(e.vars||e).palette.text.disabled},[`&.${cT.error}`]:{color:(e.vars||e).palette.error.main}},t.size==="small"&&{marginTop:4},t.contained&&{marginLeft:14,marginRight:14})),CU=uk.forwardRef(function(t,r){let o=Y({props:t,name:"MuiFormHelperText"}),{children:n,className:s,component:i="p"}=o,a=k(o,TU),l=wr(),p=no({props:o,muiFormControl:l,states:["variant","size","disabled","error","filled","focused","required"]}),c=d({},o,{component:i,contained:p.variant==="filled"||p.variant==="outlined",variant:p.variant,size:p.size,disabled:p.disabled,error:p.error,filled:p.filled,focused:p.focused,required:p.required}),u=bU(c);return(0,uT.jsx)(PU,d({as:i,ownerState:c,className:A(u.root,s),ref:r},a,{children:n===" "?ck||(ck=(0,uT.jsx)("span",{className:"notranslate",children:"\u200B"})):n}))}),dT=CU;J();var zl=P(L());var Dk=P(Wt());J();var Ok=P(ni()),Ze=P(L());J();var zs=P(L());J();var Vr=P(L());J();var qm=P(L());function dk(e){return K("MuiList",e)}var mme=W("MuiList",["root","padding","dense","subheader"]);var fk=P(H()),mk=P(H()),$U=["children","className","component","dense","disablePadding","subheader"],wU=e=>{let{classes:t,disablePadding:r,dense:o,subheader:n}=e;return G({root:["root",!r&&"padding",o&&"dense",n&&"subheader"]},dk,t)},_U=M("ul",{name:"MuiList",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,!r.disablePadding&&t.padding,r.dense&&t.dense,r.subheader&&t.subheader]}})(({ownerState:e})=>d({listStyle:"none",margin:0,padding:0,position:"relative"},!e.disablePadding&&{paddingTop:8,paddingBottom:8},e.subheader&&{paddingTop:0})),RU=qm.forwardRef(function(t,r){let o=Y({props:t,name:"MuiList"}),{children:n,className:s,component:i="ul",dense:a=!1,disablePadding:l=!1,subheader:p}=o,c=k(o,$U),u=qm.useMemo(()=>({dense:a}),[a]),f=d({},o,{component:i,dense:a,disablePadding:l}),v=wU(f);return(0,mk.jsx)(jc.Provider,{value:u,children:(0,fk.jsxs)(_U,d({as:i,className:A(v.root,s),ref:r,ownerState:f},c,{children:[p,n]}))})}),fT=RU;var yk=Ti;var gk=P(H()),EU=["actions","autoFocus","autoFocusItem","children","className","disabledItemsFocusable","disableListWrap","onKeyDown","variant"];function mT(e,t,r){return e===t?e.firstChild:t&&t.nextElementSibling?t.nextElementSibling:r?null:e.firstChild}function hk(e,t,r){return e===t?r?e.firstChild:e.lastChild:t&&t.previousElementSibling?t.previousElementSibling:r?null:e.lastChild}function vk(e,t){if(t===void 0)return!0;let r=e.innerText;return r===void 0&&(r=e.textContent),r=r.trim().toLowerCase(),r.length===0?!1:t.repeating?r[0]===t.keys[0]:r.indexOf(t.keys.join(""))===0}function Wc(e,t,r,o,n,s){let i=!1,a=n(e,t,t?r:!1);for(;a;){if(a===e.firstChild){if(i)return!1;i=!0}let l=o?!1:a.disabled||a.getAttribute("aria-disabled")==="true";if(!a.hasAttribute("tabindex")||!vk(a,s)||l)a=n(e,a,r);else return a.focus(),!0}return!1}var SU=Vr.forwardRef(function(t,r){let{actions:o,autoFocus:n=!1,autoFocusItem:s=!1,children:i,className:a,disabledItemsFocusable:l=!1,disableListWrap:p=!1,onKeyDown:c,variant:u="selectedMenu"}=t,f=k(t,EU),v=Vr.useRef(null),x=Vr.useRef({keys:[],repeating:!0,previousKeyMatched:!0,lastTime:null});Sl(()=>{n&&v.current.focus()},[n]),Vr.useImperativeHandle(o,()=>({adjustStyleForScrollbar:(g,{direction:T})=>{let w=!v.current.style.width;if(g.clientHeight<v.current.clientHeight&&w){let $=`${yk(Ms(g))}px`;v.current.style[T==="rtl"?"paddingLeft":"paddingRight"]=$,v.current.style.width=`calc(100% + ${$})`}return v.current}}),[]);let h=g=>{let T=v.current,w=g.key,$=Ms(T).activeElement;if(w==="ArrowDown")g.preventDefault(),Wc(T,$,p,l,mT);else if(w==="ArrowUp")g.preventDefault(),Wc(T,$,p,l,hk);else if(w==="Home")g.preventDefault(),Wc(T,null,p,l,mT);else if(w==="End")g.preventDefault(),Wc(T,null,p,l,hk);else if(w.length===1){let C=x.current,_=w.toLowerCase(),S=performance.now();C.keys.length>0&&(S-C.lastTime>500?(C.keys=[],C.repeating=!0,C.previousKeyMatched=!0):C.repeating&&_!==C.keys[0]&&(C.repeating=!1)),C.lastTime=S,C.keys.push(_);let R=$&&!C.repeating&&vk($,C);C.previousKeyMatched&&(R||Wc(T,$,!1,l,mT,C))?g.preventDefault():C.previousKeyMatched=!1}c&&c(g)},b=Qe(v,r),y=-1;Vr.Children.forEach(i,(g,T)=>{if(!Vr.isValidElement(g)){y===T&&(y+=1,y>=i.length&&(y=-1));return}g.props.disabled||(u==="selectedMenu"&&g.props.selected||y===-1)&&(y=T),y===T&&(g.props.disabled||g.props.muiSkipListHighlight||g.type.muiSkipListHighlight)&&(y+=1,y>=i.length&&(y=-1))});let m=Vr.Children.map(i,(g,T)=>{if(T===y){let w={};return s&&(w.autoFocus=!0),g.props.tabIndex===void 0&&u==="selectedMenu"&&(w.tabIndex=0),Vr.cloneElement(g,w)}return g});return(0,gk.jsx)(fT,d({role:"menu",ref:b,className:a,onKeyDown:h,tabIndex:n?0:-1},f,{children:m}))}),yT=SU;J();var tr=P(L());function xk(e){return K("MuiPopover",e)}var Ume=W("MuiPopover",["root","paper"]);var Km=P(H()),kU=["onEntering"],OU=["action","anchorEl","anchorOrigin","anchorPosition","anchorReference","children","className","container","elevation","marginThreshold","open","PaperProps","slots","slotProps","transformOrigin","TransitionComponent","transitionDuration","TransitionProps","disableScrollLock"],NU=["slotProps"];function Tk(e,t){let r=0;return typeof t=="number"?r=t:t==="center"?r=e.height/2:t==="bottom"&&(r=e.height),r}function bk(e,t){let r=0;return typeof t=="number"?r=t:t==="center"?r=e.width/2:t==="right"&&(r=e.width),r}function Pk(e){return[e.horizontal,e.vertical].map(t=>typeof t=="number"?`${t}px`:t).join(" ")}function hT(e){return typeof e=="function"?e():e}var MU=e=>{let{classes:t}=e;return G({root:["root"],paper:["paper"]},xk,t)},IU=M(Di,{name:"MuiPopover",slot:"Root",overridesResolver:(e,t)=>t.root})({}),gT=M(cr,{name:"MuiPopover",slot:"Paper",overridesResolver:(e,t)=>t.paper})({position:"absolute",overflowY:"auto",overflowX:"hidden",minWidth:16,minHeight:16,maxWidth:"calc(100% - 32px)",maxHeight:"calc(100% - 32px)",outline:0}),jU=tr.forwardRef(function(t,r){var o,n,s;let i=Y({props:t,name:"MuiPopover"}),{action:a,anchorEl:l,anchorOrigin:p={vertical:"top",horizontal:"left"},anchorPosition:c,anchorReference:u="anchorEl",children:f,className:v,container:x,elevation:h=8,marginThreshold:b=16,open:y,PaperProps:m={},slots:g,slotProps:T,transformOrigin:w={vertical:"top",horizontal:"left"},TransitionComponent:$=js,transitionDuration:C="auto",TransitionProps:{onEntering:_}={},disableScrollLock:S=!1}=i,R=k(i.TransitionProps,kU),j=k(i,OU),U=(o=T?.paper)!=null?o:m,z=tr.useRef(),Z=Qe(z,U.ref),B=d({},i,{anchorOrigin:p,anchorReference:u,elevation:h,marginThreshold:b,externalPaperSlotProps:U,transformOrigin:w,TransitionComponent:$,transitionDuration:C,TransitionProps:R}),D=MU(B),q=tr.useCallback(()=>{if(u==="anchorPosition")return c;let re=hT(l),ge=(re&&re.nodeType===1?re:Ms(z.current).body).getBoundingClientRect();return{top:ge.top+Tk(ge,p.vertical),left:ge.left+bk(ge,p.horizontal)}},[l,p.horizontal,p.vertical,c,u]),E=tr.useCallback(re=>({vertical:Tk(re,w.vertical),horizontal:bk(re,w.horizontal)}),[w.horizontal,w.vertical]),F=tr.useCallback(re=>{let de={width:re.offsetWidth,height:re.offsetHeight},ge=E(de);if(u==="none")return{top:null,left:null,transformOrigin:Pk(ge)};let yr=q(),Kt=yr.top-ge.vertical,wt=yr.left-ge.horizontal,or=Kt+de.height,Je=wt+de.width,Ie=Ai(hT(l)),Gt=Ie.innerHeight-b,vt=Ie.innerWidth-b;if(b!==null&&Kt<b){let Oe=Kt-b;Kt-=Oe,ge.vertical+=Oe}else if(b!==null&&or>Gt){let Oe=or-Gt;Kt-=Oe,ge.vertical+=Oe}if(b!==null&&wt<b){let Oe=wt-b;wt-=Oe,ge.horizontal+=Oe}else if(Je>vt){let Oe=Je-vt;wt-=Oe,ge.horizontal+=Oe}return{top:`${Math.round(Kt)}px`,left:`${Math.round(wt)}px`,transformOrigin:Pk(ge)}},[l,u,q,E,b]),[ae,ye]=tr.useState(y),me=tr.useCallback(()=>{let re=z.current;if(!re)return;let de=F(re);de.top!==null&&(re.style.top=de.top),de.left!==null&&(re.style.left=de.left),re.style.transformOrigin=de.transformOrigin,ye(!0)},[F]);tr.useEffect(()=>(S&&window.addEventListener("scroll",me),()=>window.removeEventListener("scroll",me)),[l,S,me]);let te=(re,de)=>{_&&_(re,de),me()},ne=()=>{ye(!1)};tr.useEffect(()=>{y&&me()}),tr.useImperativeHandle(a,()=>y?{updatePosition:()=>{me()}}:null,[y,me]),tr.useEffect(()=>{if(!y)return;let re=Sm(()=>{me()}),de=Ai(l);return de.addEventListener("resize",re),()=>{re.clear(),de.removeEventListener("resize",re)}},[l,y,me]);let ue=C;C==="auto"&&!$.muiSupportAuto&&(ue=void 0);let he=x||(l?Ms(hT(l)).body:void 0),be=(n=g?.root)!=null?n:IU,Te=(s=g?.paper)!=null?s:gT,Pe=zr({elementType:Te,externalSlotProps:d({},U,{style:ae?U.style:d({},U.style,{opacity:0})}),additionalProps:{elevation:h,ref:Z},ownerState:B,className:A(D.paper,U?.className)}),Ke=zr({elementType:be,externalSlotProps:T?.root||{},externalForwardedProps:j,additionalProps:{ref:r,slotProps:{backdrop:{invisible:!0}},container:he,open:y},ownerState:B,className:A(D.root,v)}),{slotProps:N}=Ke,V=k(Ke,NU);return(0,Km.jsx)(be,d({},V,!ws(be)&&{slotProps:N,disableScrollLock:S},{children:(0,Km.jsx)($,d({appear:!0,in:y,onEntering:te,onExited:ne,timeout:ue},R,{children:(0,Km.jsx)(Te,d({},Pe,{children:f}))}))}))}),vT=jU;function Ck(e){return K("MuiMenu",e)}var fye=W("MuiMenu",["root","paper","list"]);var xT=P(H()),DU=["onEntering"],LU=["autoFocus","children","className","disableAutoFocusItem","MenuListProps","onClose","open","PaperProps","PopoverClasses","transitionDuration","TransitionProps","variant","slots","slotProps"],AU={vertical:"top",horizontal:"right"},zU={vertical:"top",horizontal:"left"},BU=e=>{let{classes:t}=e;return G({root:["root"],paper:["paper"],list:["list"]},Ck,t)},FU=M(vT,{shouldForwardProp:e=>je(e)||e==="classes",name:"MuiMenu",slot:"Root",overridesResolver:(e,t)=>t.root})({}),UU=M(gT,{name:"MuiMenu",slot:"Paper",overridesResolver:(e,t)=>t.paper})({maxHeight:"calc(100% - 96px)",WebkitOverflowScrolling:"touch"}),WU=M(yT,{name:"MuiMenu",slot:"List",overridesResolver:(e,t)=>t.list})({outline:0}),VU=zs.forwardRef(function(t,r){var o,n;let s=Y({props:t,name:"MuiMenu"}),{autoFocus:i=!0,children:a,className:l,disableAutoFocusItem:p=!1,MenuListProps:c={},onClose:u,open:f,PaperProps:v={},PopoverClasses:x,transitionDuration:h="auto",TransitionProps:{onEntering:b}={},variant:y="selectedMenu",slots:m={},slotProps:g={}}=s,T=k(s.TransitionProps,DU),w=k(s,LU),$=Rs(),C=d({},s,{autoFocus:i,disableAutoFocusItem:p,MenuListProps:c,onEntering:b,PaperProps:v,transitionDuration:h,TransitionProps:T,variant:y}),_=BU(C),S=i&&!p&&f,R=zs.useRef(null),j=(E,F)=>{R.current&&R.current.adjustStyleForScrollbar(E,{direction:$?"rtl":"ltr"}),b&&b(E,F)},U=E=>{E.key==="Tab"&&(E.preventDefault(),u&&u(E,"tabKeyDown"))},z=-1;zs.Children.map(a,(E,F)=>{zs.isValidElement(E)&&(E.props.disabled||(y==="selectedMenu"&&E.props.selected||z===-1)&&(z=F))});let Z=(o=m.paper)!=null?o:UU,B=(n=g.paper)!=null?n:v,D=zr({elementType:m.root,externalSlotProps:g.root,ownerState:C,className:[_.root,l]}),q=zr({elementType:Z,externalSlotProps:B,ownerState:C,className:_.paper});return(0,xT.jsx)(FU,d({onClose:u,anchorOrigin:{vertical:"bottom",horizontal:$?"right":"left"},transformOrigin:$?AU:zU,slots:{paper:Z,root:m.root},slotProps:{root:D,paper:q},open:f,ref:r,transitionDuration:h,TransitionProps:d({onEntering:j},T),ownerState:C},w,{classes:x,children:(0,xT.jsx)(WU,d({onKeyDown:U,actions:R,autoFocus:i&&(z===-1||p),autoFocusItem:S,variant:y},c,{className:A(_.list,c.className),children:a}))}))}),$k=VU;J();var Ym=P(L());function wk(e){return K("MuiNativeSelect",e)}var HU=W("MuiNativeSelect",["root","select","multiple","filled","outlined","standard","disabled","icon","iconOpen","iconFilled","iconOutlined","iconStandard","nativeInput","error"]),Gm=HU;var TT=P(H()),_k=P(H()),qU=["className","disabled","error","IconComponent","inputRef","variant"],KU=e=>{let{classes:t,variant:r,disabled:o,multiple:n,open:s,error:i}=e,a={select:["select",r,o&&"disabled",n&&"multiple",i&&"error"],icon:["icon",`icon${I(r)}`,s&&"iconOpen",o&&"disabled"]};return G(a,wk,t)},bT=({ownerState:e,theme:t})=>d({MozAppearance:"none",WebkitAppearance:"none",userSelect:"none",borderRadius:0,cursor:"pointer","&:focus":d({},t.vars?{backgroundColor:`rgba(${t.vars.palette.common.onBackgroundChannel} / 0.05)`}:{backgroundColor:t.palette.mode==="light"?"rgba(0, 0, 0, 0.05)":"rgba(255, 255, 255, 0.05)"},{borderRadius:0}),"&::-ms-expand":{display:"none"},[`&.${Gm.disabled}`]:{cursor:"default"},"&[multiple]":{height:"auto"},"&:not([multiple]) option, &:not([multiple]) optgroup":{backgroundColor:(t.vars||t).palette.background.paper},"&&&":{paddingRight:24,minWidth:16}},e.variant==="filled"&&{"&&&":{paddingRight:32}},e.variant==="outlined"&&{borderRadius:(t.vars||t).shape.borderRadius,"&:focus":{borderRadius:(t.vars||t).shape.borderRadius},"&&&":{paddingRight:32}}),GU=M("select",{name:"MuiNativeSelect",slot:"Select",shouldForwardProp:je,overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.select,t[r.variant],r.error&&t.error,{[`&.${Gm.multiple}`]:t.multiple}]}})(bT),PT=({ownerState:e,theme:t})=>d({position:"absolute",right:0,top:"calc(50% - .5em)",pointerEvents:"none",color:(t.vars||t).palette.action.active,[`&.${Gm.disabled}`]:{color:(t.vars||t).palette.action.disabled}},e.open&&{transform:"rotate(180deg)"},e.variant==="filled"&&{right:7},e.variant==="outlined"&&{right:7}),YU=M("svg",{name:"MuiNativeSelect",slot:"Icon",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.icon,r.variant&&t[`icon${I(r.variant)}`],r.open&&t.iconOpen]}})(PT),XU=Ym.forwardRef(function(t,r){let{className:o,disabled:n,error:s,IconComponent:i,inputRef:a,variant:l="standard"}=t,p=k(t,qU),c=d({},t,{disabled:n,variant:l,error:s}),u=KU(c);return(0,_k.jsxs)(Ym.Fragment,{children:[(0,TT.jsx)(GU,d({ownerState:c,className:A(u.select,o),disabled:n,ref:a||r},p)),t.multiple?null:(0,TT.jsx)(YU,{as:i,ownerState:c,className:u.icon})]})}),Rk=XU;function Ek(e){return K("MuiSelect",e)}var QU=W("MuiSelect",["root","select","multiple","filled","outlined","standard","disabled","focused","icon","iconOpen","iconFilled","iconOutlined","iconStandard","nativeInput","error"]),Ll=QU;var Al=P(H()),Nk=P(H()),Sk,ZU=["aria-describedby","aria-label","autoFocus","autoWidth","children","className","defaultOpen","defaultValue","disabled","displayEmpty","error","IconComponent","inputRef","labelId","MenuProps","multiple","name","onBlur","onChange","onClose","onFocus","onOpen","open","readOnly","renderValue","SelectDisplayProps","tabIndex","type","value","variant"],JU=M("div",{name:"MuiSelect",slot:"Select",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[{[`&.${Ll.select}`]:t.select},{[`&.${Ll.select}`]:t[r.variant]},{[`&.${Ll.error}`]:t.error},{[`&.${Ll.multiple}`]:t.multiple}]}})(bT,{[`&.${Ll.select}`]:{height:"auto",minHeight:"1.4375em",textOverflow:"ellipsis",whiteSpace:"nowrap",overflow:"hidden"}}),e6=M("svg",{name:"MuiSelect",slot:"Icon",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.icon,r.variant&&t[`icon${I(r.variant)}`],r.open&&t.iconOpen]}})(PT),t6=M("input",{shouldForwardProp:e=>bc(e)&&e!=="classes",name:"MuiSelect",slot:"NativeInput",overridesResolver:(e,t)=>t.nativeInput})({bottom:0,left:0,position:"absolute",opacity:0,pointerEvents:"none",width:"100%",boxSizing:"border-box"});function kk(e,t){return typeof t=="object"&&t!==null?e===t:String(e)===String(t)}function r6(e){return e==null||typeof e=="string"&&!e.trim()}var o6=e=>{let{classes:t,variant:r,disabled:o,multiple:n,open:s,error:i}=e,a={select:["select",r,o&&"disabled",n&&"multiple",i&&"error"],icon:["icon",`icon${I(r)}`,s&&"iconOpen",o&&"disabled"],nativeInput:["nativeInput"]};return G(a,Ek,t)},n6=Ze.forwardRef(function(t,r){var o;let{"aria-describedby":n,"aria-label":s,autoFocus:i,autoWidth:a,children:l,className:p,defaultOpen:c,defaultValue:u,disabled:f,displayEmpty:v,error:x=!1,IconComponent:h,inputRef:b,labelId:y,MenuProps:m={},multiple:g,name:T,onBlur:w,onChange:$,onClose:C,onFocus:_,onOpen:S,open:R,readOnly:j,renderValue:U,SelectDisplayProps:z={},tabIndex:Z,value:B,variant:D="standard"}=t,q=k(t,ZU),[E,F]=ji({controlled:B,default:u,name:"Select"}),[ae,ye]=ji({controlled:R,default:c,name:"Select"}),me=Ze.useRef(null),te=Ze.useRef(null),[ne,ue]=Ze.useState(null),{current:he}=Ze.useRef(R!=null),[be,Te]=Ze.useState(),Pe=Qe(r,b),Ke=Ze.useCallback(le=>{te.current=le,le&&ue(le)},[]),N=ne?.parentNode;Ze.useImperativeHandle(Pe,()=>({focus:()=>{te.current.focus()},node:me.current,value:E}),[E]),Ze.useEffect(()=>{c&&ae&&ne&&!he&&(Te(a?null:N.clientWidth),te.current.focus())},[ne,a]),Ze.useEffect(()=>{i&&te.current.focus()},[i]),Ze.useEffect(()=>{if(!y)return;let le=Ms(te.current).getElementById(y);if(le){let $e=()=>{getSelection().isCollapsed&&te.current.focus()};return le.addEventListener("click",$e),()=>{le.removeEventListener("click",$e)}}},[y]);let V=(le,$e)=>{le?S&&S($e):C&&C($e),he||(Te(a?null:N.clientWidth),ye(le))},re=le=>{le.button===0&&(le.preventDefault(),te.current.focus(),V(!0,le))},de=le=>{V(!1,le)},ge=Ze.Children.toArray(l),yr=le=>{let $e=ge.find(ft=>ft.props.value===le.target.value);$e!==void 0&&(F($e.props.value),$&&$(le,$e))},Kt=le=>$e=>{let ft;if($e.currentTarget.hasAttribute("tabindex")){if(g){ft=Array.isArray(E)?E.slice():[];let rn=E.indexOf(le.props.value);rn===-1?ft.push(le.props.value):ft.splice(rn,1)}else ft=le.props.value;if(le.props.onClick&&le.props.onClick($e),E!==ft&&(F(ft),$)){let rn=$e.nativeEvent||$e,Gl=new rn.constructor(rn.type,rn);Object.defineProperty(Gl,"target",{writable:!0,value:{value:ft,name:T}}),$(Gl,le)}g||V(!1,$e)}},wt=le=>{j||[" ","ArrowUp","ArrowDown","Enter"].indexOf(le.key)!==-1&&(le.preventDefault(),V(!0,le))},or=ne!==null&&ae,Je=le=>{!or&&w&&(Object.defineProperty(le,"target",{writable:!0,value:{value:E,name:T}}),w(le))};delete q["aria-invalid"];let Ie,Gt,vt=[],Oe=!1,Yt=!1;(Ui({value:E})||v)&&(U?Ie=U(E):Oe=!0);let hr=ge.map(le=>{if(!Ze.isValidElement(le))return null;let $e;if(g){if(!Array.isArray(E))throw new Error((0,Ok.default)(2));$e=E.some(ft=>kk(ft,le.props.value)),$e&&Oe&&vt.push(le.props.children)}else $e=kk(E,le.props.value),$e&&Oe&&(Gt=le.props.children);return $e&&(Yt=!0),Ze.cloneElement(le,{"aria-selected":$e?"true":"false",onClick:Kt(le),onKeyUp:ft=>{ft.key===" "&&ft.preventDefault(),le.props.onKeyUp&&le.props.onKeyUp(ft)},role:"option",selected:$e,value:void 0,"data-value":le.props.value})});Oe&&(g?vt.length===0?Ie=null:Ie=vt.reduce((le,$e,ft)=>(le.push($e),ft<vt.length-1&&le.push(", "),le),[]):Ie=Gt);let Or=be;!a&&he&&ne&&(Or=N.clientWidth);let Se;typeof Z<"u"?Se=Z:Se=f?null:0;let ce=z.id||(T?`mui-component-select-${T}`:void 0),_t=d({},t,{variant:D,value:E,open:or,error:x}),xn=o6(_t),so=d({},m.PaperProps,(o=m.slotProps)==null?void 0:o.paper),Xn=To();return(0,Nk.jsxs)(Ze.Fragment,{children:[(0,Al.jsx)(JU,d({ref:Ke,tabIndex:Se,role:"combobox","aria-controls":Xn,"aria-disabled":f?"true":void 0,"aria-expanded":or?"true":"false","aria-haspopup":"listbox","aria-label":s,"aria-labelledby":[y,ce].filter(Boolean).join(" ")||void 0,"aria-describedby":n,onKeyDown:wt,onMouseDown:f||j?null:re,onBlur:Je,onFocus:_},z,{ownerState:_t,className:A(z.className,xn.select,p),id:ce,children:r6(Ie)?Sk||(Sk=(0,Al.jsx)("span",{className:"notranslate",children:"\u200B"})):Ie})),(0,Al.jsx)(t6,d({"aria-invalid":x,value:Array.isArray(E)?E.join(","):E,name:T,ref:me,"aria-hidden":!0,onChange:yr,tabIndex:-1,disabled:f,className:xn.nativeInput,autoFocus:i,ownerState:_t},q)),(0,Al.jsx)(e6,{as:h,className:xn.icon,ownerState:_t}),(0,Al.jsx)($k,d({id:`menu-${T||""}`,anchorEl:N,open:or,onClose:de,anchorOrigin:{vertical:"bottom",horizontal:"center"},transformOrigin:{vertical:"top",horizontal:"center"}},m,{MenuListProps:d({"aria-labelledby":y,role:"listbox","aria-multiselectable":g?"true":void 0,disableListWrap:!0,id:Xn},m.MenuListProps),slotProps:d({},m.slotProps,{paper:d({},so,{style:d({minWidth:Or},so!=null?so.style:null)})}),children:hr}))]})}),Mk=n6;var rhe=P(L());var Ik=P(H()),jk=Pt((0,Ik.jsx)("path",{d:"M7 10l5 5 5-5z"}),"ArrowDropDown");var Vc=P(H()),s6=["autoWidth","children","classes","className","defaultOpen","displayEmpty","IconComponent","id","input","inputProps","label","labelId","MenuProps","multiple","native","onClose","onOpen","open","renderValue","SelectDisplayProps","variant"],i6=["root"],a6=e=>{let{classes:t}=e;return t},CT={name:"MuiSelect",overridesResolver:(e,t)=>t.root,shouldForwardProp:e=>je(e)&&e!=="variant",slot:"Root"},l6=M(zc,CT)(""),p6=M(Uc,CT)(""),c6=M(Bc,CT)(""),Lk=zl.forwardRef(function(t,r){let o=Y({name:"MuiSelect",props:t}),{autoWidth:n=!1,children:s,classes:i={},className:a,defaultOpen:l=!1,displayEmpty:p=!1,IconComponent:c=jk,id:u,input:f,inputProps:v,label:x,labelId:h,MenuProps:b,multiple:y=!1,native:m=!1,onClose:g,onOpen:T,open:w,renderValue:$,SelectDisplayProps:C,variant:_="outlined"}=o,S=k(o,s6),R=m?Rk:Mk,j=wr(),U=no({props:o,muiFormControl:j,states:["variant","error"]}),z=U.variant||_,Z=d({},o,{variant:z,classes:i}),B=a6(Z),D=k(B,i6),q=f||{standard:(0,Vc.jsx)(l6,{ownerState:Z}),outlined:(0,Vc.jsx)(p6,{label:x,ownerState:Z}),filled:(0,Vc.jsx)(c6,{ownerState:Z})}[z],E=Qe(r,Mt(q));return(0,Vc.jsx)(zl.Fragment,{children:zl.cloneElement(q,d({inputComponent:R,inputProps:d({children:s,error:U.error,IconComponent:c,variant:z,type:void 0,multiple:y},m?{id:u}:{autoWidth:n,defaultOpen:l,displayEmpty:p,labelId:h,MenuProps:b,onClose:g,onOpen:T,open:w,renderValue:$,SelectDisplayProps:d({id:u},C)},v,{classes:v?(0,Dk.default)(D,v.classes):D},f?f.props.inputProps:{})},(y&&m||p)&&z==="outlined"?{notched:!0}:{},{ref:E,className:A(q.props.className,a,B.root)},!f&&{variant:z},S))})});Lk.muiName="Select";var $T=Lk;function Ak(e){return K("MuiTextField",e)}var _he=W("MuiTextField",["root"]);var Hc=P(H()),Bk=P(H()),u6=["autoComplete","autoFocus","children","className","color","defaultValue","disabled","error","FormHelperTextProps","fullWidth","helperText","id","InputLabelProps","inputProps","InputProps","inputRef","label","maxRows","minRows","multiline","name","onBlur","onChange","onFocus","placeholder","required","rows","select","SelectProps","type","value","variant"],d6={standard:zc,filled:Bc,outlined:Uc},f6=e=>{let{classes:t}=e;return G({root:["root"]},Ak,t)},m6=M(pT,{name:"MuiTextField",slot:"Root",overridesResolver:(e,t)=>t.root})({}),y6=zk.forwardRef(function(t,r){let o=Y({props:t,name:"MuiTextField"}),{autoComplete:n,autoFocus:s=!1,children:i,className:a,color:l="primary",defaultValue:p,disabled:c=!1,error:u=!1,FormHelperTextProps:f,fullWidth:v=!1,helperText:x,id:h,InputLabelProps:b,inputProps:y,InputProps:m,inputRef:g,label:T,maxRows:w,minRows:$,multiline:C=!1,name:_,onBlur:S,onChange:R,onFocus:j,placeholder:U,required:z=!1,rows:Z,select:B=!1,SelectProps:D,type:q,value:E,variant:F="outlined"}=o,ae=k(o,u6),ye=d({},o,{autoFocus:s,color:l,disabled:c,error:u,fullWidth:v,multiline:C,required:z,select:B,variant:F}),me=f6(ye),te={};F==="outlined"&&(b&&typeof b.shrink<"u"&&(te.notched=b.shrink),te.label=T),B&&((!D||!D.native)&&(te.id=void 0),te["aria-describedby"]=void 0);let ne=To(h),ue=x&&ne?`${ne}-helper-text`:void 0,he=T&&ne?`${ne}-label`:void 0,be=d6[F],Te=(0,Hc.jsx)(be,d({"aria-describedby":ue,autoComplete:n,autoFocus:s,defaultValue:p,fullWidth:v,multiline:C,name:_,rows:Z,maxRows:w,minRows:$,type:q,value:E,id:ne,inputRef:g,onBlur:S,onChange:R,onFocus:j,placeholder:U,inputProps:y},te,m));return(0,Bk.jsxs)(m6,d({className:A(me.root,a),disabled:c,error:u,fullWidth:v,ref:r,required:z,color:l,variant:F,ownerState:ye},ae,{children:[T!=null&&T!==""&&(0,Hc.jsx)(aT,d({htmlFor:ne,id:he},b,{children:T})),B?(0,Hc.jsx)($T,d({"aria-describedby":ue,id:ne,labelId:he,value:E,input:Te},D,{children:i})):Te,x&&(0,Hc.jsx)(dT,d({id:ue},f,{children:x}))]}))}),Hr=y6;J();var Uk=P(L());function Fk(e){return K("MuiToolbar",e)}var Yhe=W("MuiToolbar",["root","gutters","regular","dense"]);var Wk=P(H()),h6=["className","component","disableGutters","variant"],g6=e=>{let{classes:t,disableGutters:r,variant:o}=e;return G({root:["root",!r&&"gutters",o]},Fk,t)},v6=M("div",{name:"MuiToolbar",slot:"Root",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.root,!r.disableGutters&&t.gutters,t[r.variant]]}})(({theme:e,ownerState:t})=>d({position:"relative",display:"flex",alignItems:"center"},!t.disableGutters&&{paddingLeft:e.spacing(2),paddingRight:e.spacing(2),[e.breakpoints.up("sm")]:{paddingLeft:e.spacing(3),paddingRight:e.spacing(3)}},t.variant==="dense"&&{minHeight:48}),({theme:e,ownerState:t})=>t.variant==="regular"&&e.mixins.toolbar),x6=Uk.forwardRef(function(t,r){let o=Y({props:t,name:"MuiToolbar"}),{className:n,component:s="div",disableGutters:i=!1,variant:a="regular"}=o,l=k(o,h6),p=d({},o,{component:s,disableGutters:i,variant:a}),c=g6(p);return(0,Wk.jsx)(v6,d({as:s,className:A(c.root,n),ref:r,ownerState:p},l))}),Xm=x6;J();var $t=P(L());var FT=P($r());J();var yO=P(Hk());var hO=P(L());J();var fr=P(L());var gt="top",jt="bottom",St="right",Ct="left",Zm="auto",Bs=[gt,jt,St,Ct],Hn="start",Gi="end",qk="clippingParents",Jm="viewport",Bl="popper",Kk="reference",wT=Bs.reduce(function(e,t){return e.concat([t+"-"+Hn,t+"-"+Gi])},[]),ey=[].concat(Bs,[Zm]).reduce(function(e,t){return e.concat([t,t+"-"+Hn,t+"-"+Gi])},[]),w6="beforeRead",_6="read",R6="afterRead",E6="beforeMain",S6="main",k6="afterMain",O6="beforeWrite",N6="write",M6="afterWrite",Gk=[w6,_6,R6,E6,S6,k6,O6,N6,M6];function Ht(e){return e?(e.nodeName||"").toLowerCase():null}function st(e){if(e==null)return window;if(e.toString()!=="[object Window]"){var t=e.ownerDocument;return t&&t.defaultView||window}return e}function No(e){var t=st(e).Element;return e instanceof t||e instanceof Element}function Dt(e){var t=st(e).HTMLElement;return e instanceof t||e instanceof HTMLElement}function Fl(e){if(typeof ShadowRoot>"u")return!1;var t=st(e).ShadowRoot;return e instanceof t||e instanceof ShadowRoot}function I6(e){var t=e.state;Object.keys(t.elements).forEach(function(r){var o=t.styles[r]||{},n=t.attributes[r]||{},s=t.elements[r];!Dt(s)||!Ht(s)||(Object.assign(s.style,o),Object.keys(n).forEach(function(i){var a=n[i];a===!1?s.removeAttribute(i):s.setAttribute(i,a===!0?"":a)}))})}function j6(e){var t=e.state,r={popper:{position:t.options.strategy,left:"0",top:"0",margin:"0"},arrow:{position:"absolute"},reference:{}};return Object.assign(t.elements.popper.style,r.popper),t.styles=r,t.elements.arrow&&Object.assign(t.elements.arrow.style,r.arrow),function(){Object.keys(t.elements).forEach(function(o){var n=t.elements[o],s=t.attributes[o]||{},i=Object.keys(t.styles.hasOwnProperty(o)?t.styles[o]:r[o]),a=i.reduce(function(l,p){return l[p]="",l},{});!Dt(n)||!Ht(n)||(Object.assign(n.style,a),Object.keys(s).forEach(function(l){n.removeAttribute(l)}))})}}var Yk={name:"applyStyles",enabled:!0,phase:"write",fn:I6,effect:j6,requires:["computeStyles"]};function qt(e){return e.split("-")[0]}var Zo=Math.max,Yi=Math.min,qn=Math.round;function Ul(){var e=navigator.userAgentData;return e!=null&&e.brands&&Array.isArray(e.brands)?e.brands.map(function(t){return t.brand+"/"+t.version}).join(" "):navigator.userAgent}function qc(){return!/^((?!chrome|android).)*safari/i.test(Ul())}function Mo(e,t,r){t===void 0&&(t=!1),r===void 0&&(r=!1);var o=e.getBoundingClientRect(),n=1,s=1;t&&Dt(e)&&(n=e.offsetWidth>0&&qn(o.width)/e.offsetWidth||1,s=e.offsetHeight>0&&qn(o.height)/e.offsetHeight||1);var i=No(e)?st(e):window,a=i.visualViewport,l=!qc()&&r,p=(o.left+(l&&a?a.offsetLeft:0))/n,c=(o.top+(l&&a?a.offsetTop:0))/s,u=o.width/n,f=o.height/s;return{width:u,height:f,top:c,right:p+u,bottom:c+f,left:p,x:p,y:c}}function Xi(e){var t=Mo(e),r=e.offsetWidth,o=e.offsetHeight;return Math.abs(t.width-r)<=1&&(r=t.width),Math.abs(t.height-o)<=1&&(o=t.height),{x:e.offsetLeft,y:e.offsetTop,width:r,height:o}}function Kc(e,t){var r=t.getRootNode&&t.getRootNode();if(e.contains(t))return!0;if(r&&Fl(r)){var o=t;do{if(o&&e.isSameNode(o))return!0;o=o.parentNode||o.host}while(o)}return!1}function kr(e){return st(e).getComputedStyle(e)}function _T(e){return["table","td","th"].indexOf(Ht(e))>=0}function rr(e){return((No(e)?e.ownerDocument:e.document)||window.document).documentElement}function Kn(e){return Ht(e)==="html"?e:e.assignedSlot||e.parentNode||(Fl(e)?e.host:null)||rr(e)}function Xk(e){return!Dt(e)||kr(e).position==="fixed"?null:e.offsetParent}function D6(e){var t=/firefox/i.test(Ul()),r=/Trident/i.test(Ul());if(r&&Dt(e)){var o=kr(e);if(o.position==="fixed")return null}var n=Kn(e);for(Fl(n)&&(n=n.host);Dt(n)&&["html","body"].indexOf(Ht(n))<0;){var s=kr(n);if(s.transform!=="none"||s.perspective!=="none"||s.contain==="paint"||["transform","perspective"].indexOf(s.willChange)!==-1||t&&s.willChange==="filter"||t&&s.filter&&s.filter!=="none")return n;n=n.parentNode}return null}function Jo(e){for(var t=st(e),r=Xk(e);r&&_T(r)&&kr(r).position==="static";)r=Xk(r);return r&&(Ht(r)==="html"||Ht(r)==="body"&&kr(r).position==="static")?t:r||D6(e)||t}function Qi(e){return["top","bottom"].indexOf(e)>=0?"x":"y"}function Zi(e,t,r){return Zo(e,Yi(t,r))}function Qk(e,t,r){var o=Zi(e,t,r);return o>r?r:o}function Gc(){return{top:0,right:0,bottom:0,left:0}}function Yc(e){return Object.assign({},Gc(),e)}function Xc(e,t){return t.reduce(function(r,o){return r[o]=e,r},{})}var L6=function(t,r){return t=typeof t=="function"?t(Object.assign({},r.rects,{placement:r.placement})):t,Yc(typeof t!="number"?t:Xc(t,Bs))};function A6(e){var t,r=e.state,o=e.name,n=e.options,s=r.elements.arrow,i=r.modifiersData.popperOffsets,a=qt(r.placement),l=Qi(a),p=[Ct,St].indexOf(a)>=0,c=p?"height":"width";if(!(!s||!i)){var u=L6(n.padding,r),f=Xi(s),v=l==="y"?gt:Ct,x=l==="y"?jt:St,h=r.rects.reference[c]+r.rects.reference[l]-i[l]-r.rects.popper[c],b=i[l]-r.rects.reference[l],y=Jo(s),m=y?l==="y"?y.clientHeight||0:y.clientWidth||0:0,g=h/2-b/2,T=u[v],w=m-f[c]-u[x],$=m/2-f[c]/2+g,C=Zi(T,$,w),_=l;r.modifiersData[o]=(t={},t[_]=C,t.centerOffset=C-$,t)}}function z6(e){var t=e.state,r=e.options,o=r.element,n=o===void 0?"[data-popper-arrow]":o;n!=null&&(typeof n=="string"&&(n=t.elements.popper.querySelector(n),!n)||Kc(t.elements.popper,n)&&(t.elements.arrow=n))}var Zk={name:"arrow",enabled:!0,phase:"main",fn:A6,effect:z6,requires:["popperOffsets"],requiresIfExists:["preventOverflow"]};function Io(e){return e.split("-")[1]}var B6={top:"auto",right:"auto",bottom:"auto",left:"auto"};function F6(e,t){var r=e.x,o=e.y,n=t.devicePixelRatio||1;return{x:qn(r*n)/n||0,y:qn(o*n)/n||0}}function Jk(e){var t,r=e.popper,o=e.popperRect,n=e.placement,s=e.variation,i=e.offsets,a=e.position,l=e.gpuAcceleration,p=e.adaptive,c=e.roundOffsets,u=e.isFixed,f=i.x,v=f===void 0?0:f,x=i.y,h=x===void 0?0:x,b=typeof c=="function"?c({x:v,y:h}):{x:v,y:h};v=b.x,h=b.y;var y=i.hasOwnProperty("x"),m=i.hasOwnProperty("y"),g=Ct,T=gt,w=window;if(p){var $=Jo(r),C="clientHeight",_="clientWidth";if($===st(r)&&($=rr(r),kr($).position!=="static"&&a==="absolute"&&(C="scrollHeight",_="scrollWidth")),$=$,n===gt||(n===Ct||n===St)&&s===Gi){T=jt;var S=u&&$===w&&w.visualViewport?w.visualViewport.height:$[C];h-=S-o.height,h*=l?1:-1}if(n===Ct||(n===gt||n===jt)&&s===Gi){g=St;var R=u&&$===w&&w.visualViewport?w.visualViewport.width:$[_];v-=R-o.width,v*=l?1:-1}}var j=Object.assign({position:a},p&&B6),U=c===!0?F6({x:v,y:h},st(r)):{x:v,y:h};if(v=U.x,h=U.y,l){var z;return Object.assign({},j,(z={},z[T]=m?"0":"",z[g]=y?"0":"",z.transform=(w.devicePixelRatio||1)<=1?"translate("+v+"px, "+h+"px)":"translate3d("+v+"px, "+h+"px, 0)",z))}return Object.assign({},j,(t={},t[T]=m?h+"px":"",t[g]=y?v+"px":"",t.transform="",t))}function U6(e){var t=e.state,r=e.options,o=r.gpuAcceleration,n=o===void 0?!0:o,s=r.adaptive,i=s===void 0?!0:s,a=r.roundOffsets,l=a===void 0?!0:a,p={placement:qt(t.placement),variation:Io(t.placement),popper:t.elements.popper,popperRect:t.rects.popper,gpuAcceleration:n,isFixed:t.options.strategy==="fixed"};t.modifiersData.popperOffsets!=null&&(t.styles.popper=Object.assign({},t.styles.popper,Jk(Object.assign({},p,{offsets:t.modifiersData.popperOffsets,position:t.options.strategy,adaptive:i,roundOffsets:l})))),t.modifiersData.arrow!=null&&(t.styles.arrow=Object.assign({},t.styles.arrow,Jk(Object.assign({},p,{offsets:t.modifiersData.arrow,position:"absolute",adaptive:!1,roundOffsets:l})))),t.attributes.popper=Object.assign({},t.attributes.popper,{"data-popper-placement":t.placement})}var eO={name:"computeStyles",enabled:!0,phase:"beforeWrite",fn:U6,data:{}};var ty={passive:!0};function W6(e){var t=e.state,r=e.instance,o=e.options,n=o.scroll,s=n===void 0?!0:n,i=o.resize,a=i===void 0?!0:i,l=st(t.elements.popper),p=[].concat(t.scrollParents.reference,t.scrollParents.popper);return s&&p.forEach(function(c){c.addEventListener("scroll",r.update,ty)}),a&&l.addEventListener("resize",r.update,ty),function(){s&&p.forEach(function(c){c.removeEventListener("scroll",r.update,ty)}),a&&l.removeEventListener("resize",r.update,ty)}}var tO={name:"eventListeners",enabled:!0,phase:"write",fn:function(){},effect:W6,data:{}};var V6={left:"right",right:"left",bottom:"top",top:"bottom"};function Wl(e){return e.replace(/left|right|bottom|top/g,function(t){return V6[t]})}var H6={start:"end",end:"start"};function ry(e){return e.replace(/start|end/g,function(t){return H6[t]})}function Ji(e){var t=st(e),r=t.pageXOffset,o=t.pageYOffset;return{scrollLeft:r,scrollTop:o}}function ea(e){return Mo(rr(e)).left+Ji(e).scrollLeft}function RT(e,t){var r=st(e),o=rr(e),n=r.visualViewport,s=o.clientWidth,i=o.clientHeight,a=0,l=0;if(n){s=n.width,i=n.height;var p=qc();(p||!p&&t==="fixed")&&(a=n.offsetLeft,l=n.offsetTop)}return{width:s,height:i,x:a+ea(e),y:l}}function ET(e){var t,r=rr(e),o=Ji(e),n=(t=e.ownerDocument)==null?void 0:t.body,s=Zo(r.scrollWidth,r.clientWidth,n?n.scrollWidth:0,n?n.clientWidth:0),i=Zo(r.scrollHeight,r.clientHeight,n?n.scrollHeight:0,n?n.clientHeight:0),a=-o.scrollLeft+ea(e),l=-o.scrollTop;return kr(n||r).direction==="rtl"&&(a+=Zo(r.clientWidth,n?n.clientWidth:0)-s),{width:s,height:i,x:a,y:l}}function ta(e){var t=kr(e),r=t.overflow,o=t.overflowX,n=t.overflowY;return/auto|scroll|overlay|hidden/.test(r+n+o)}function oy(e){return["html","body","#document"].indexOf(Ht(e))>=0?e.ownerDocument.body:Dt(e)&&ta(e)?e:oy(Kn(e))}function Fs(e,t){var r;t===void 0&&(t=[]);var o=oy(e),n=o===((r=e.ownerDocument)==null?void 0:r.body),s=st(o),i=n?[s].concat(s.visualViewport||[],ta(o)?o:[]):o,a=t.concat(i);return n?a:a.concat(Fs(Kn(i)))}function Vl(e){return Object.assign({},e,{left:e.x,top:e.y,right:e.x+e.width,bottom:e.y+e.height})}function q6(e,t){var r=Mo(e,!1,t==="fixed");return r.top=r.top+e.clientTop,r.left=r.left+e.clientLeft,r.bottom=r.top+e.clientHeight,r.right=r.left+e.clientWidth,r.width=e.clientWidth,r.height=e.clientHeight,r.x=r.left,r.y=r.top,r}function rO(e,t,r){return t===Jm?Vl(RT(e,r)):No(t)?q6(t,r):Vl(ET(rr(e)))}function K6(e){var t=Fs(Kn(e)),r=["absolute","fixed"].indexOf(kr(e).position)>=0,o=r&&Dt(e)?Jo(e):e;return No(o)?t.filter(function(n){return No(n)&&Kc(n,o)&&Ht(n)!=="body"}):[]}function ST(e,t,r,o){var n=t==="clippingParents"?K6(e):[].concat(t),s=[].concat(n,[r]),i=s[0],a=s.reduce(function(l,p){var c=rO(e,p,o);return l.top=Zo(c.top,l.top),l.right=Yi(c.right,l.right),l.bottom=Yi(c.bottom,l.bottom),l.left=Zo(c.left,l.left),l},rO(e,i,o));return a.width=a.right-a.left,a.height=a.bottom-a.top,a.x=a.left,a.y=a.top,a}function Qc(e){var t=e.reference,r=e.element,o=e.placement,n=o?qt(o):null,s=o?Io(o):null,i=t.x+t.width/2-r.width/2,a=t.y+t.height/2-r.height/2,l;switch(n){case gt:l={x:i,y:t.y-r.height};break;case jt:l={x:i,y:t.y+t.height};break;case St:l={x:t.x+t.width,y:a};break;case Ct:l={x:t.x-r.width,y:a};break;default:l={x:t.x,y:t.y}}var p=n?Qi(n):null;if(p!=null){var c=p==="y"?"height":"width";switch(s){case Hn:l[p]=l[p]-(t[c]/2-r[c]/2);break;case Gi:l[p]=l[p]+(t[c]/2-r[c]/2);break;default:}}return l}function en(e,t){t===void 0&&(t={});var r=t,o=r.placement,n=o===void 0?e.placement:o,s=r.strategy,i=s===void 0?e.strategy:s,a=r.boundary,l=a===void 0?qk:a,p=r.rootBoundary,c=p===void 0?Jm:p,u=r.elementContext,f=u===void 0?Bl:u,v=r.altBoundary,x=v===void 0?!1:v,h=r.padding,b=h===void 0?0:h,y=Yc(typeof b!="number"?b:Xc(b,Bs)),m=f===Bl?Kk:Bl,g=e.rects.popper,T=e.elements[x?m:f],w=ST(No(T)?T:T.contextElement||rr(e.elements.popper),l,c,i),$=Mo(e.elements.reference),C=Qc({reference:$,element:g,strategy:"absolute",placement:n}),_=Vl(Object.assign({},g,C)),S=f===Bl?_:$,R={top:w.top-S.top+y.top,bottom:S.bottom-w.bottom+y.bottom,left:w.left-S.left+y.left,right:S.right-w.right+y.right},j=e.modifiersData.offset;if(f===Bl&&j){var U=j[n];Object.keys(R).forEach(function(z){var Z=[St,jt].indexOf(z)>=0?1:-1,B=[gt,jt].indexOf(z)>=0?"y":"x";R[z]+=U[B]*Z})}return R}function kT(e,t){t===void 0&&(t={});var r=t,o=r.placement,n=r.boundary,s=r.rootBoundary,i=r.padding,a=r.flipVariations,l=r.allowedAutoPlacements,p=l===void 0?ey:l,c=Io(o),u=c?a?wT:wT.filter(function(x){return Io(x)===c}):Bs,f=u.filter(function(x){return p.indexOf(x)>=0});f.length===0&&(f=u);var v=f.reduce(function(x,h){return x[h]=en(e,{placement:h,boundary:n,rootBoundary:s,padding:i})[qt(h)],x},{});return Object.keys(v).sort(function(x,h){return v[x]-v[h]})}function G6(e){if(qt(e)===Zm)return[];var t=Wl(e);return[ry(e),t,ry(t)]}function Y6(e){var t=e.state,r=e.options,o=e.name;if(!t.modifiersData[o]._skip){for(var n=r.mainAxis,s=n===void 0?!0:n,i=r.altAxis,a=i===void 0?!0:i,l=r.fallbackPlacements,p=r.padding,c=r.boundary,u=r.rootBoundary,f=r.altBoundary,v=r.flipVariations,x=v===void 0?!0:v,h=r.allowedAutoPlacements,b=t.options.placement,y=qt(b),m=y===b,g=l||(m||!x?[Wl(b)]:G6(b)),T=[b].concat(g).reduce(function(ne,ue){return ne.concat(qt(ue)===Zm?kT(t,{placement:ue,boundary:c,rootBoundary:u,padding:p,flipVariations:x,allowedAutoPlacements:h}):ue)},[]),w=t.rects.reference,$=t.rects.popper,C=new Map,_=!0,S=T[0],R=0;R<T.length;R++){var j=T[R],U=qt(j),z=Io(j)===Hn,Z=[gt,jt].indexOf(U)>=0,B=Z?"width":"height",D=en(t,{placement:j,boundary:c,rootBoundary:u,altBoundary:f,padding:p}),q=Z?z?St:Ct:z?jt:gt;w[B]>$[B]&&(q=Wl(q));var E=Wl(q),F=[];if(s&&F.push(D[U]<=0),a&&F.push(D[q]<=0,D[E]<=0),F.every(function(ne){return ne})){S=j,_=!1;break}C.set(j,F)}if(_)for(var ae=x?3:1,ye=function(ue){var he=T.find(function(be){var Te=C.get(be);if(Te)return Te.slice(0,ue).every(function(Pe){return Pe})});if(he)return S=he,"break"},me=ae;me>0;me--){var te=ye(me);if(te==="break")break}t.placement!==S&&(t.modifiersData[o]._skip=!0,t.placement=S,t.reset=!0)}}var oO={name:"flip",enabled:!0,phase:"main",fn:Y6,requiresIfExists:["offset"],data:{_skip:!1}};function nO(e,t,r){return r===void 0&&(r={x:0,y:0}),{top:e.top-t.height-r.y,right:e.right-t.width+r.x,bottom:e.bottom-t.height+r.y,left:e.left-t.width-r.x}}function sO(e){return[gt,St,jt,Ct].some(function(t){return e[t]>=0})}function X6(e){var t=e.state,r=e.name,o=t.rects.reference,n=t.rects.popper,s=t.modifiersData.preventOverflow,i=en(t,{elementContext:"reference"}),a=en(t,{altBoundary:!0}),l=nO(i,o),p=nO(a,n,s),c=sO(l),u=sO(p);t.modifiersData[r]={referenceClippingOffsets:l,popperEscapeOffsets:p,isReferenceHidden:c,hasPopperEscaped:u},t.attributes.popper=Object.assign({},t.attributes.popper,{"data-popper-reference-hidden":c,"data-popper-escaped":u})}var iO={name:"hide",enabled:!0,phase:"main",requiresIfExists:["preventOverflow"],fn:X6};function Q6(e,t,r){var o=qt(e),n=[Ct,gt].indexOf(o)>=0?-1:1,s=typeof r=="function"?r(Object.assign({},t,{placement:e})):r,i=s[0],a=s[1];return i=i||0,a=(a||0)*n,[Ct,St].indexOf(o)>=0?{x:a,y:i}:{x:i,y:a}}function Z6(e){var t=e.state,r=e.options,o=e.name,n=r.offset,s=n===void 0?[0,0]:n,i=ey.reduce(function(c,u){return c[u]=Q6(u,t.rects,s),c},{}),a=i[t.placement],l=a.x,p=a.y;t.modifiersData.popperOffsets!=null&&(t.modifiersData.popperOffsets.x+=l,t.modifiersData.popperOffsets.y+=p),t.modifiersData[o]=i}var aO={name:"offset",enabled:!0,phase:"main",requires:["popperOffsets"],fn:Z6};function J6(e){var t=e.state,r=e.name;t.modifiersData[r]=Qc({reference:t.rects.reference,element:t.rects.popper,strategy:"absolute",placement:t.placement})}var lO={name:"popperOffsets",enabled:!0,phase:"read",fn:J6,data:{}};function OT(e){return e==="x"?"y":"x"}function eW(e){var t=e.state,r=e.options,o=e.name,n=r.mainAxis,s=n===void 0?!0:n,i=r.altAxis,a=i===void 0?!1:i,l=r.boundary,p=r.rootBoundary,c=r.altBoundary,u=r.padding,f=r.tether,v=f===void 0?!0:f,x=r.tetherOffset,h=x===void 0?0:x,b=en(t,{boundary:l,rootBoundary:p,padding:u,altBoundary:c}),y=qt(t.placement),m=Io(t.placement),g=!m,T=Qi(y),w=OT(T),$=t.modifiersData.popperOffsets,C=t.rects.reference,_=t.rects.popper,S=typeof h=="function"?h(Object.assign({},t.rects,{placement:t.placement})):h,R=typeof S=="number"?{mainAxis:S,altAxis:S}:Object.assign({mainAxis:0,altAxis:0},S),j=t.modifiersData.offset?t.modifiersData.offset[t.placement]:null,U={x:0,y:0};if($){if(s){var z,Z=T==="y"?gt:Ct,B=T==="y"?jt:St,D=T==="y"?"height":"width",q=$[T],E=q+b[Z],F=q-b[B],ae=v?-_[D]/2:0,ye=m===Hn?C[D]:_[D],me=m===Hn?-_[D]:-C[D],te=t.elements.arrow,ne=v&&te?Xi(te):{width:0,height:0},ue=t.modifiersData["arrow#persistent"]?t.modifiersData["arrow#persistent"].padding:Gc(),he=ue[Z],be=ue[B],Te=Zi(0,C[D],ne[D]),Pe=g?C[D]/2-ae-Te-he-R.mainAxis:ye-Te-he-R.mainAxis,Ke=g?-C[D]/2+ae+Te+be+R.mainAxis:me+Te+be+R.mainAxis,N=t.elements.arrow&&Jo(t.elements.arrow),V=N?T==="y"?N.clientTop||0:N.clientLeft||0:0,re=(z=j?.[T])!=null?z:0,de=q+Pe-re-V,ge=q+Ke-re,yr=Zi(v?Yi(E,de):E,q,v?Zo(F,ge):F);$[T]=yr,U[T]=yr-q}if(a){var Kt,wt=T==="x"?gt:Ct,or=T==="x"?jt:St,Je=$[w],Ie=w==="y"?"height":"width",Gt=Je+b[wt],vt=Je-b[or],Oe=[gt,Ct].indexOf(y)!==-1,Yt=(Kt=j?.[w])!=null?Kt:0,hr=Oe?Gt:Je-C[Ie]-_[Ie]-Yt+R.altAxis,Or=Oe?Je+C[Ie]+_[Ie]-Yt-R.altAxis:vt,Se=v&&Oe?Qk(hr,Je,Or):Zi(v?hr:Gt,Je,v?Or:vt);$[w]=Se,U[w]=Se-Je}t.modifiersData[o]=U}}var pO={name:"preventOverflow",enabled:!0,phase:"main",fn:eW,requiresIfExists:["offset"]};function NT(e){return{scrollLeft:e.scrollLeft,scrollTop:e.scrollTop}}function MT(e){return e===st(e)||!Dt(e)?Ji(e):NT(e)}function tW(e){var t=e.getBoundingClientRect(),r=qn(t.width)/e.offsetWidth||1,o=qn(t.height)/e.offsetHeight||1;return r!==1||o!==1}function IT(e,t,r){r===void 0&&(r=!1);var o=Dt(t),n=Dt(t)&&tW(t),s=rr(t),i=Mo(e,n,r),a={scrollLeft:0,scrollTop:0},l={x:0,y:0};return(o||!o&&!r)&&((Ht(t)!=="body"||ta(s))&&(a=MT(t)),Dt(t)?(l=Mo(t,!0),l.x+=t.clientLeft,l.y+=t.clientTop):s&&(l.x=ea(s))),{x:i.left+a.scrollLeft-l.x,y:i.top+a.scrollTop-l.y,width:i.width,height:i.height}}function rW(e){var t=new Map,r=new Set,o=[];e.forEach(function(s){t.set(s.name,s)});function n(s){r.add(s.name);var i=[].concat(s.requires||[],s.requiresIfExists||[]);i.forEach(function(a){if(!r.has(a)){var l=t.get(a);l&&n(l)}}),o.push(s)}return e.forEach(function(s){r.has(s.name)||n(s)}),o}function jT(e){var t=rW(e);return Gk.reduce(function(r,o){return r.concat(t.filter(function(n){return n.phase===o}))},[])}function DT(e){var t;return function(){return t||(t=new Promise(function(r){Promise.resolve().then(function(){t=void 0,r(e())})})),t}}function LT(e){var t=e.reduce(function(r,o){var n=r[o.name];return r[o.name]=n?Object.assign({},n,o,{options:Object.assign({},n.options,o.options),data:Object.assign({},n.data,o.data)}):o,r},{});return Object.keys(t).map(function(r){return t[r]})}var cO={placement:"bottom",modifiers:[],strategy:"absolute"};function uO(){for(var e=arguments.length,t=new Array(e),r=0;r<e;r++)t[r]=arguments[r];return!t.some(function(o){return!(o&&typeof o.getBoundingClientRect=="function")})}function dO(e){e===void 0&&(e={});var t=e,r=t.defaultModifiers,o=r===void 0?[]:r,n=t.defaultOptions,s=n===void 0?cO:n;return function(a,l,p){p===void 0&&(p=s);var c={placement:"bottom",orderedModifiers:[],options:Object.assign({},cO,s),modifiersData:{},elements:{reference:a,popper:l},attributes:{},styles:{}},u=[],f=!1,v={state:c,setOptions:function(y){var m=typeof y=="function"?y(c.options):y;h(),c.options=Object.assign({},s,c.options,m),c.scrollParents={reference:No(a)?Fs(a):a.contextElement?Fs(a.contextElement):[],popper:Fs(l)};var g=jT(LT([].concat(o,c.options.modifiers)));return c.orderedModifiers=g.filter(function(T){return T.enabled}),x(),v.update()},forceUpdate:function(){if(!f){var y=c.elements,m=y.reference,g=y.popper;if(uO(m,g)){c.rects={reference:IT(m,Jo(g),c.options.strategy==="fixed"),popper:Xi(g)},c.reset=!1,c.placement=c.options.placement,c.orderedModifiers.forEach(function(R){return c.modifiersData[R.name]=Object.assign({},R.data)});for(var T=0;T<c.orderedModifiers.length;T++){if(c.reset===!0){c.reset=!1,T=-1;continue}var w=c.orderedModifiers[T],$=w.fn,C=w.options,_=C===void 0?{}:C,S=w.name;typeof $=="function"&&(c=$({state:c,options:_,name:S,instance:v})||c)}}}},update:DT(function(){return new Promise(function(b){v.forceUpdate(),b(c)})}),destroy:function(){h(),f=!0}};if(!uO(a,l))return v;v.setOptions(p).then(function(b){!f&&p.onFirstUpdate&&p.onFirstUpdate(b)});function x(){c.orderedModifiers.forEach(function(b){var y=b.name,m=b.options,g=m===void 0?{}:m,T=b.effect;if(typeof T=="function"){var w=T({state:c,name:y,instance:v,options:g}),$=function(){};u.push(w||$)}})}function h(){u.forEach(function(b){return b()}),u=[]}return v}}var oW=[tO,lO,eO,Yk,aO,oO,pO,Zk,iO],AT=dO({defaultModifiers:oW});function fO(e){return K("MuiPopper",e)}var sbe=W("MuiPopper",["root"]);var ny=P(H()),nW=["anchorEl","children","direction","disablePortal","modifiers","open","placement","popperOptions","popperRef","slotProps","slots","TransitionProps","ownerState"],sW=["anchorEl","children","container","direction","disablePortal","keepMounted","modifiers","open","placement","popperOptions","popperRef","style","transition","slotProps","slots"];function iW(e,t){if(t==="ltr")return e;switch(e){case"bottom-end":return"bottom-start";case"bottom-start":return"bottom-end";case"top-end":return"top-start";case"top-start":return"top-end";default:return e}}function zT(e){return typeof e=="function"?e():e}function aW(e){return e.nodeType!==void 0}var lW=e=>{let{classes:t}=e;return G({root:["root"]},fO,t)},pW={},cW=fr.forwardRef(function(t,r){var o;let{anchorEl:n,children:s,direction:i,disablePortal:a,modifiers:l,open:p,placement:c,popperOptions:u,popperRef:f,slotProps:v={},slots:x={},TransitionProps:h}=t,b=k(t,nW),y=fr.useRef(null),m=yt(y,r),g=fr.useRef(null),T=yt(g,f),w=fr.useRef(T);Nt(()=>{w.current=T},[T]),fr.useImperativeHandle(f,()=>g.current,[]);let $=iW(c,i),[C,_]=fr.useState($),[S,R]=fr.useState(zT(n));fr.useEffect(()=>{g.current&&g.current.forceUpdate()}),fr.useEffect(()=>{n&&R(zT(n))},[n]),Nt(()=>{if(!S||!p)return;let B=E=>{_(E.placement)},D=[{name:"preventOverflow",options:{altBoundary:a}},{name:"flip",options:{altBoundary:a}},{name:"onUpdate",enabled:!0,phase:"afterWrite",fn:({state:E})=>{B(E)}}];l!=null&&(D=D.concat(l)),u&&u.modifiers!=null&&(D=D.concat(u.modifiers));let q=AT(S,y.current,d({placement:$},u,{modifiers:D}));return w.current(q),()=>{q.destroy(),w.current(null)}},[S,a,l,p,u,$]);let j={placement:C};h!==null&&(j.TransitionProps=h);let U=lW(t),z=(o=x.root)!=null?o:"div",Z=zr({elementType:z,externalSlotProps:v.root,externalForwardedProps:b,additionalProps:{role:"tooltip",ref:m},ownerState:t,className:U.root});return(0,ny.jsx)(z,d({},Z,{children:typeof s=="function"?s(j):s}))}),uW=fr.forwardRef(function(t,r){let{anchorEl:o,children:n,container:s,direction:i="ltr",disablePortal:a=!1,keepMounted:l=!1,modifiers:p,open:c,placement:u="bottom",popperOptions:f=pW,popperRef:v,style:x,transition:h=!1,slotProps:b={},slots:y={}}=t,m=k(t,sW),[g,T]=fr.useState(!0),w=()=>{T(!1)},$=()=>{T(!0)};if(!l&&!c&&(!h||g))return null;let C;if(s)C=s;else if(o){let R=zT(o);C=R&&aW(R)?rt(R).body:rt(null).body}let _=!c&&l&&(!h||g)?"none":void 0,S=h?{in:c,onEnter:w,onExited:$}:void 0;return(0,ny.jsx)(Nc,{disablePortal:a,container:C,children:(0,ny.jsx)(cW,d({anchorEl:o,direction:i,disablePortal:a,modifiers:p,ref:r,open:h?!g:c,placement:u,popperOptions:f,popperRef:v,slotProps:b,slots:y},m,{style:d({position:"fixed",top:0,left:0,display:_},x),TransitionProps:S,children:n}))})}),mO=uW;var gO=P(H()),dW=["anchorEl","component","components","componentsProps","container","disablePortal","keepMounted","modifiers","open","placement","popperOptions","popperRef","transition","slots","slotProps"],fW=M(mO,{name:"MuiPopper",slot:"Root",overridesResolver:(e,t)=>t.root})({}),mW=hO.forwardRef(function(t,r){var o;let n=(0,yO.default)(),s=Y({props:t,name:"MuiPopper"}),{anchorEl:i,component:a,components:l,componentsProps:p,container:c,disablePortal:u,keepMounted:f,modifiers:v,open:x,placement:h,popperOptions:b,popperRef:y,transition:m,slots:g,slotProps:T}=s,w=k(s,dW),$=(o=g?.root)!=null?o:l?.Root,C=d({anchorEl:i,container:c,disablePortal:u,keepMounted:f,modifiers:v,open:x,placement:h,popperOptions:b,popperRef:y,transition:m},w);return(0,gO.jsx)(fW,d({as:a,direction:n?.direction,slots:{root:$},slotProps:T??p},C,{ref:r}))}),sy=mW;function vO(e){return K("MuiTooltip",e)}var yW=W("MuiTooltip",["popper","popperInteractive","popperArrow","popperClose","tooltip","tooltipArrow","touch","tooltipPlacementLeft","tooltipPlacementRight","tooltipPlacementTop","tooltipPlacementBottom","arrow"]),Gn=yW;var Jc=P(H()),BT=P(H()),hW=["arrow","children","classes","components","componentsProps","describeChild","disableFocusListener","disableHoverListener","disableInteractive","disableTouchListener","enterDelay","enterNextDelay","enterTouchDelay","followCursor","id","leaveDelay","leaveTouchDelay","onClose","onOpen","open","placement","PopperComponent","PopperProps","slotProps","slots","title","TransitionComponent","TransitionProps"];function gW(e){return Math.round(e*1e5)/1e5}var vW=e=>{let{classes:t,disableInteractive:r,arrow:o,touch:n,placement:s}=e,i={popper:["popper",!r&&"popperInteractive",o&&"popperArrow"],tooltip:["tooltip",o&&"tooltipArrow",n&&"touch",`tooltipPlacement${I(s.split("-")[0])}`],arrow:["arrow"]};return G(i,vO,t)},xW=M(sy,{name:"MuiTooltip",slot:"Popper",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.popper,!r.disableInteractive&&t.popperInteractive,r.arrow&&t.popperArrow,!r.open&&t.popperClose]}})(({theme:e,ownerState:t,open:r})=>d({zIndex:(e.vars||e).zIndex.tooltip,pointerEvents:"none"},!t.disableInteractive&&{pointerEvents:"auto"},!r&&{pointerEvents:"none"},t.arrow&&{[`&[data-popper-placement*="bottom"] .${Gn.arrow}`]:{top:0,marginTop:"-0.71em","&::before":{transformOrigin:"0 100%"}},[`&[data-popper-placement*="top"] .${Gn.arrow}`]:{bottom:0,marginBottom:"-0.71em","&::before":{transformOrigin:"100% 0"}},[`&[data-popper-placement*="right"] .${Gn.arrow}`]:d({},t.isRtl?{right:0,marginRight:"-0.71em"}:{left:0,marginLeft:"-0.71em"},{height:"1em",width:"0.71em","&::before":{transformOrigin:"100% 100%"}}),[`&[data-popper-placement*="left"] .${Gn.arrow}`]:d({},t.isRtl?{left:0,marginLeft:"-0.71em"}:{right:0,marginRight:"-0.71em"},{height:"1em",width:"0.71em","&::before":{transformOrigin:"0 0"}})})),TW=M("div",{name:"MuiTooltip",slot:"Tooltip",overridesResolver:(e,t)=>{let{ownerState:r}=e;return[t.tooltip,r.touch&&t.touch,r.arrow&&t.tooltipArrow,t[`tooltipPlacement${I(r.placement.split("-")[0])}`]]}})(({theme:e,ownerState:t})=>d({backgroundColor:e.vars?e.vars.palette.Tooltip.bg:(0,FT.alpha)(e.palette.grey[700],.92),borderRadius:(e.vars||e).shape.borderRadius,color:(e.vars||e).palette.common.white,fontFamily:e.typography.fontFamily,padding:"4px 8px",fontSize:e.typography.pxToRem(11),maxWidth:300,margin:2,wordWrap:"break-word",fontWeight:e.typography.fontWeightMedium},t.arrow&&{position:"relative",margin:0},t.touch&&{padding:"8px 16px",fontSize:e.typography.pxToRem(14),lineHeight:`${gW(16/14)}em`,fontWeight:e.typography.fontWeightRegular},{[`.${Gn.popper}[data-popper-placement*="left"] &`]:d({transformOrigin:"right center"},t.isRtl?d({marginLeft:"14px"},t.touch&&{marginLeft:"24px"}):d({marginRight:"14px"},t.touch&&{marginRight:"24px"})),[`.${Gn.popper}[data-popper-placement*="right"] &`]:d({transformOrigin:"left center"},t.isRtl?d({marginRight:"14px"},t.touch&&{marginRight:"24px"}):d({marginLeft:"14px"},t.touch&&{marginLeft:"24px"})),[`.${Gn.popper}[data-popper-placement*="top"] &`]:d({transformOrigin:"center bottom",marginBottom:"14px"},t.touch&&{marginBottom:"24px"}),[`.${Gn.popper}[data-popper-placement*="bottom"] &`]:d({transformOrigin:"center top",marginTop:"14px"},t.touch&&{marginTop:"24px"})})),bW=M("span",{name:"MuiTooltip",slot:"Arrow",overridesResolver:(e,t)=>t.arrow})(({theme:e})=>({overflow:"hidden",position:"absolute",width:"1em",height:"0.71em",boxSizing:"border-box",color:e.vars?e.vars.palette.Tooltip.bg:(0,FT.alpha)(e.palette.grey[700],.9),"&::before":{content:'""',margin:"auto",display:"block",width:"100%",height:"100%",backgroundColor:"currentColor",transform:"rotate(45deg)"}})),iy=!1,xO=new jn,Zc={x:0,y:0};function ay(e,t){return(r,...o)=>{t&&t(r,...o),e(r,...o)}}var PW=$t.forwardRef(function(t,r){var o,n,s,i,a,l,p,c,u,f,v,x,h,b,y,m,g,T,w;let $=Y({props:t,name:"MuiTooltip"}),{arrow:C=!1,children:_,components:S={},componentsProps:R={},describeChild:j=!1,disableFocusListener:U=!1,disableHoverListener:z=!1,disableInteractive:Z=!1,disableTouchListener:B=!1,enterDelay:D=100,enterNextDelay:q=0,enterTouchDelay:E=700,followCursor:F=!1,id:ae,leaveDelay:ye=0,leaveTouchDelay:me=1500,onClose:te,onOpen:ne,open:ue,placement:he="bottom",PopperComponent:be,PopperProps:Te={},slotProps:Pe={},slots:Ke={},title:N,TransitionComponent:V=js,TransitionProps:re}=$,de=k($,hW),ge=$t.isValidElement(_)?_:(0,Jc.jsx)("span",{children:_}),yr=pr(),Kt=Rs(),[wt,or]=$t.useState(),[Je,Ie]=$t.useState(null),Gt=$t.useRef(!1),vt=Z||F,Oe=Ar(),Yt=Ar(),hr=Ar(),Or=Ar(),[Se,ce]=ji({controlled:ue,default:!1,name:"Tooltip",state:"open"}),_t=Se,xn=UE(ae),so=$t.useRef(),Xn=ks(()=>{so.current!==void 0&&(document.body.style.WebkitUserSelect=so.current,so.current=void 0),Or.clear()});$t.useEffect(()=>Xn,[Xn]);let le=ve=>{xO.clear(),iy=!0,ce(!0),ne&&!_t&&ne(ve)},$e=ks(ve=>{xO.start(800+ye,()=>{iy=!1}),ce(!1),te&&_t&&te(ve),Oe.start(yr.transitions.duration.shortest,()=>{Gt.current=!1})}),ft=ve=>{Gt.current&&ve.type!=="touchstart"||(wt&&wt.removeAttribute("title"),Yt.clear(),hr.clear(),D||iy&&q?Yt.start(iy?q:D,()=>{le(ve)}):le(ve))},rn=ve=>{Yt.clear(),hr.start(ye,()=>{$e(ve)})},{isFocusVisibleRef:Gl,onBlur:FO,onFocus:UO,ref:WO}=im(),[,ZT]=$t.useState(!1),JT=ve=>{FO(ve),Gl.current===!1&&(ZT(!1),rn(ve))},eb=ve=>{wt||or(ve.currentTarget),UO(ve),Gl.current===!0&&(ZT(!0),ft(ve))},tb=ve=>{Gt.current=!0;let qr=ge.props;qr.onTouchStart&&qr.onTouchStart(ve)},VO=ve=>{tb(ve),hr.clear(),Oe.clear(),Xn(),so.current=document.body.style.WebkitUserSelect,document.body.style.WebkitUserSelect="none",Or.start(E,()=>{document.body.style.WebkitUserSelect=so.current,ft(ve)})},HO=ve=>{ge.props.onTouchEnd&&ge.props.onTouchEnd(ve),Xn(),hr.start(me,()=>{$e(ve)})};$t.useEffect(()=>{if(!_t)return;function ve(qr){(qr.key==="Escape"||qr.key==="Esc")&&$e(qr)}return document.addEventListener("keydown",ve),()=>{document.removeEventListener("keydown",ve)}},[$e,_t]);let qO=Qe(Mt(ge),WO,or,r);!N&&N!==0&&(_t=!1);let uy=$t.useRef(),KO=ve=>{let qr=ge.props;qr.onMouseMove&&qr.onMouseMove(ve),Zc={x:ve.clientX,y:ve.clientY},uy.current&&uy.current.update()},Yl={},dy=typeof N=="string";j?(Yl.title=!_t&&dy&&!z?N:null,Yl["aria-describedby"]=_t?xn:null):(Yl["aria-label"]=dy?N:null,Yl["aria-labelledby"]=_t&&!dy?xn:null);let jo=d({},Yl,de,ge.props,{className:A(de.className,ge.props.className),onTouchStart:tb,ref:qO},F?{onMouseMove:KO}:{}),Xl={};B||(jo.onTouchStart=VO,jo.onTouchEnd=HO),z||(jo.onMouseOver=ay(ft,jo.onMouseOver),jo.onMouseLeave=ay(rn,jo.onMouseLeave),vt||(Xl.onMouseOver=ft,Xl.onMouseLeave=rn)),U||(jo.onFocus=ay(eb,jo.onFocus),jo.onBlur=ay(JT,jo.onBlur),vt||(Xl.onFocus=eb,Xl.onBlur=JT));let GO=$t.useMemo(()=>{var ve;let qr=[{name:"arrow",enabled:!!Je,options:{element:Je,padding:4}}];return(ve=Te.popperOptions)!=null&&ve.modifiers&&(qr=qr.concat(Te.popperOptions.modifiers)),d({},Te.popperOptions,{modifiers:qr})},[Je,Te]),Ql=d({},$,{isRtl:Kt,arrow:C,disableInteractive:vt,placement:he,PopperComponentProp:be,touch:Gt.current}),fy=vW(Ql),rb=(o=(n=Ke.popper)!=null?n:S.Popper)!=null?o:xW,ob=(s=(i=(a=Ke.transition)!=null?a:S.Transition)!=null?i:V)!=null?s:js,nb=(l=(p=Ke.tooltip)!=null?p:S.Tooltip)!=null?l:TW,sb=(c=(u=Ke.arrow)!=null?u:S.Arrow)!=null?c:bW,YO=mn(rb,d({},Te,(f=Pe.popper)!=null?f:R.popper,{className:A(fy.popper,Te?.className,(v=(x=Pe.popper)!=null?x:R.popper)==null?void 0:v.className)}),Ql),XO=mn(ob,d({},re,(h=Pe.transition)!=null?h:R.transition),Ql),QO=mn(nb,d({},(b=Pe.tooltip)!=null?b:R.tooltip,{className:A(fy.tooltip,(y=(m=Pe.tooltip)!=null?m:R.tooltip)==null?void 0:y.className)}),Ql),ZO=mn(sb,d({},(g=Pe.arrow)!=null?g:R.arrow,{className:A(fy.arrow,(T=(w=Pe.arrow)!=null?w:R.arrow)==null?void 0:T.className)}),Ql);return(0,BT.jsxs)($t.Fragment,{children:[$t.cloneElement(ge,jo),(0,Jc.jsx)(rb,d({as:be??sy,placement:he,anchorEl:F?{getBoundingClientRect:()=>({top:Zc.y,left:Zc.x,right:Zc.x,bottom:Zc.y,width:0,height:0})}:wt,popperRef:uy,open:wt?_t:!1,id:xn,transition:!0},Xl,YO,{popperOptions:GO,children:({TransitionProps:ve})=>(0,Jc.jsx)(ob,d({timeout:yr.transitions.duration.shorter},ve,XO,{children:(0,BT.jsxs)(nb,d({},QO,{children:[N,C?(0,Jc.jsx)(sb,d({},ZO,{ref:Ie})):null]}))}))}))]})}),eu=PW;var O=U1.bind(Q.default.createElement);var Hl=[{key:"dashboard",label:"\u603B\u89C8",description:"\u5173\u952E\u6307\u6807\u4E0E\u5FEB\u901F\u67E5\u8BE2"},{key:"subscriptions",label:"\u8BA2\u9605",description:"\u7EDF\u4E00\u7BA1\u7406\u76D1\u63A7\u89C4\u5219"},{key:"items",label:"\u5546\u54C1",description:"\u67E5\u770B\u5546\u54C1\u4E0E\u5173\u8054\u8BB0\u5F55"},{key:"runtime",label:"\u8FD0\u884C\u72B6\u6001",description:"\u68C0\u67E5 Provider \u4E0E\u6293\u53D6\u60C5\u51B5"},{key:"config",label:"\u914D\u7F6E",description:"\u7F16\u8F91\u8FD0\u884C\u65F6\u914D\u7F6E"}],Lt={cardPadding:{xs:2,md:3},pageGap:{xs:2.25,md:3},sectionGap:2.5},TO={"& .MuiInputBase-root":{alignItems:"flex-start",borderRadius:{xs:"14px",md:"16px"},border:"1px solid var(--field-border)",backgroundColor:"var(--field-bg)",transition:"background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease",paddingInline:{xs:"12px",md:"14px"},boxShadow:"none","&:hover":{backgroundColor:"var(--field-bg-hover)",borderColor:"var(--field-border-hover)"},"&.Mui-focused":{backgroundColor:"var(--field-bg-focus)",borderColor:"var(--field-border-focus)",boxShadow:"var(--field-focus-ring)"},"&.Mui-error":{borderColor:"var(--field-error-border)",boxShadow:"var(--field-error-ring)"}},"& .MuiInputBase-input":{padding:{xs:"12px 0",md:"15px 0"},fontSize:{xs:"0.9rem",md:"0.95rem"},lineHeight:1.55,color:"var(--text)"},"& .MuiInputBase-input::placeholder":{color:"var(--field-placeholder)",opacity:1},"& .MuiInputBase-inputMultiline":{paddingBlock:{xs:"12px",md:"15px"}},"& .MuiSelect-select":{minHeight:"unset",padding:{xs:"12px 24px 12px 0 !important",md:"15px 26px 15px 0 !important"}},"& .MuiSvgIcon-root":{color:"var(--field-icon)"}};function hn(...e){return e.filter(Boolean).join(" ")}function WT(){let e=window.location.hash.replace(/^#\/?/,"").trim();return Hl.some(t=>t.key===e)?e:"dashboard"}function VT(e){window.location.hash=`#/${e}`}function Ue(e){return e?new Date(e*1e3).toLocaleString("zh-CN",{hour12:!1}):"-"}function qe(e){return e==null||Number.isNaN(Number(e))?"-":`\xA5${Number(e).toFixed(2)}`}function bO(e){return e==null||Number.isNaN(Number(e))?"-":`${(Number(e)*100).toFixed(0)}%`}function ql(e){let t=Number(e);if(!Number.isFinite(t)||t<=0)return"-";if(t<60)return`${t} \u79D2`;let r=[["\u5929",86400],["\u5C0F\u65F6",3600],["\u5206\u949F",60]],o=[],n=t;for(let[s,i]of r){if(n>=i){let a=Math.floor(n/i);o.push(`${a} ${s}`),n-=a*i}if(o.length===2)break}return o.join(" ")}function PO(e){return e==null||Number.isNaN(Number(e))?"-":`${Number(e).toFixed(1)} \u5206`}function gn(e){if(e===""||e===null||e===void 0)return null;let t=Number(e);return Number.isFinite(t)?t:null}function CO(e){return Array.from(new Set(String(e||"").split(/[\s,，]+/).map(t=>t.trim().toLowerCase()).filter(Boolean)))}function $O(e,t){if(!t.length)return!1;let r=[e?.title,e?.item_id,e?.keyword,e?.description,e?.desc,e?.seller_name,e?.seller,e?.latest_event_type].filter(Boolean).join(" ").toLowerCase();return t.some(o=>r.includes(o))}var Us=typeof window<"u"&&(window.AstrBotPluginView||window.AstrBotPluginPage)||null;function wO(e,t){if(e===401){let r=new Error("\u9700\u8981\u91CD\u65B0\u767B\u5F55");throw r.code="UNAUTHORIZED",r}if(e>=400||t?.ok===!1){let r=new Error(t?.error?.message||`\u8BF7\u6C42\u5931\u8D25: ${e}`);throw r.payload=t,r}}async function CW(e,t){let r=new URL(e,"http://plugin.local"),o=r.pathname.replace(/^\/+/,""),n=(t.method||"GET").toUpperCase(),s=n==="GET"?await Us.apiGet(o,Object.fromEntries(r.searchParams)):await Us.apiPost(o,{method:n,query:Object.fromEntries(r.searchParams),body:t.body}),i=s?.body||{};return wO(Number(s?.status_code||500),i),i}async function Me(e,t={}){if(Us)return CW(e,t);let r={method:t.method||"GET",credentials:"include",headers:{}};t.body!==void 0&&(r.headers["Content-Type"]="application/json",r.body=JSON.stringify(t.body));let o=await fetch(e,r),s=(o.headers.get("content-type")||"").includes("application/json")?await o.json():{};return wO(o.status,s),s}function Kl(e,t){return e?{label:"\u542F\u7528\u4E2D",color:"success",variant:"filled"}:{label:t||"\u5DF2\u6682\u505C",color:"warning",variant:"outlined"}}function ly(e){let t=String(e||"").toUpperCase();return t==="SUCCESS"?{label:"\u6210\u529F",color:"success",variant:"filled"}:t==="FAILED"?{label:"\u5931\u8D25",color:"error",variant:"filled"}:t==="RUNNING"?{label:"\u8FD0\u884C\u4E2D",color:"primary",variant:"filled"}:{label:t||"-",color:"default",variant:"outlined"}}function _O(e){let t=String(e||"").toLowerCase();return t.includes("error")||t.includes("danger")?{label:"\u5F02\u5E38",color:"error"}:t.includes("warn")?{label:"\u8B66\u544A",color:"warning"}:{label:"\u63D0\u793A",color:"primary"}}function RO(e){let t=String(e||"").toLowerCase();return!t||t==="-"?{label:"\u672A\u6807\u8BB0\u98CE\u9669",color:"default",variant:"outlined"}:t.includes("\u9AD8")||t.includes("high")?{label:e,color:"error",variant:"filled"}:t.includes("\u4E2D")||t.includes("medium")?{label:e,color:"warning",variant:"filled"}:{label:e,color:"success",variant:"outlined"}}function tn({title:e,description:t,meta:r,action:o}){return O`
		<${Ee}
			direction=${{xs:"column",md:"row"}}
			spacing=${2}
			justifyContent="space-between"
			alignItems=${{xs:"flex-start",md:"center"}}
			className="page-header"
		>
			<${Ce} sx=${{flex:1,minWidth:0}}>
				<${ie} variant="h4">${e}<//>
				${t?O`<${ie}
							variant="body1"
							color="text.secondary"
							sx=${{mt:1}}
						>
							${t}
						<//>`:null}
				${r?O`<${ie}
							variant="caption"
							color="text.secondary"
							sx=${{mt:1,display:"block"}}
						>
							${r}
						<//>`:null}
			<//>
			${o?O`<${Ce} className="header-actions">${o}<//>`:null}
		<//>
	`}function ze({title:e,description:t,action:r,children:o,className:n=""}){return O`
		<${Tl} elevation=${0} className=${hn("surface-card",n)}>
			<${bl} sx=${{p:Lt.cardPadding}}>
				${e||t||r?O`
							<${Ee}
								direction=${{xs:"column",md:"row"}}
								spacing=${2}
								justifyContent="space-between"
								alignItems=${{xs:"flex-start",md:"center"}}
							>
								<${Ce} sx=${{flex:1,minWidth:0}}>
									${e?O`<${ie} variant="h6"
												>${e}<//
											>`:null}
									${t?O`<${ie}
												variant="body2"
												color="text.secondary"
												sx=${{mt:e?.75:0}}
											>
												${t}
											<//>`:null}
								<//>
								${r?O`<${Ce}>${r}<//>`:null}
							<//>
						`:null}
				<${Ce} sx=${{mt:e||t||r?2.5:0}}>
					${o}
				<//>
			<//>
		<//>
	`}function mr({label:e,hint:t,error:r="",wrapperSx:o,fieldSx:n,fullWidth:s=!0,InputProps:i,SelectProps:a,children:l,...p}){let c=r||t||"\xA0";return O`
		<${Ce}
			className=${hn("field-block",r&&"has-error")}
			sx=${o}
		>
			${e?O`<div className="field-label" title=${e}>${e}</div>`:null}
			<${Hr}
				...${p}
				fullWidth=${s}
				variant="standard"
				error=${!!r}
				label=${void 0}
				helperText=${void 0}
				InputProps=${{disableUnderline:!0,...i||{}}}
				SelectProps=${p.select?{variant:"standard",disableUnderline:!0,...a||{}}:a}
				sx=${[TO,n].filter(Boolean)}
			>
				${l}
			<//>
			<div
				className=${hn("field-hint",r&&"is-error",!r&&!t&&"is-empty")}
				title=${r||t||void 0}
			>
				${c}
			</div>
		<//>
	`}function vn({label:e,value:t,hint:r,tone:o="primary"}){let n={primary:"primary.main",success:"success.main",warning:"warning.main",secondary:"secondary.main"};return O`
		<${Tl}
			elevation=${0}
			className=${hn("surface-card","stat-card",`tone-${o}`)}
		>
			<${bl} sx=${{p:Lt.cardPadding}}>
				<${Ee} spacing=${1}>
					<${ie} variant="body2" color="text.secondary"
						>${e}<//
					>
					<${ie}
						variant="h5"
						sx=${{color:n[o]||"text.primary"}}
					>
						${t}
					<//>
					<${ie} variant="body2" color="text.secondary"
						>${r}<//
					>
				<//>
			<//>
		<//>
	`}function ra({items:e}){let t=(e||[]).filter(r=>r&&r.value!==void 0);return t.length?O`
		<div className="info-list">
			${t.map(r=>O`
					<div className="info-row" key=${r.label}>
						<span className="info-label">${r.label}</span>
						<span className="info-value">${r.value??"-"}</span>
					</div>
				`)}
		</div>
	`:O`<div className="empty-state compact-empty">
			暂无可展示信息
		</div>`}function At({title:e,description:t}){return O`
		<div className="empty-state">
			<div className="empty-title">${e}</div>
			<div className="empty-description">${t}</div>
		</div>
	`}function EO({items:e}){return e?.length?O`
		<div className="list-stack">
			${e.map(t=>{let r=_O(t.level);return O`
					<div
						className=${hn("alert-item",`level-${r.color}`)}
						key=${`${t.keyword}-${t.occurred_at}-${t.message}`}
					>
						<div className="alert-item-head">
							<div className="alert-item-title">
								${t.keyword||"\u7CFB\u7EDF"}
							</div>
							<${Fe}
								size="small"
								label=${r.label}
								color=${r.color}
							/>
						</div>
						<div className="alert-item-body">
							${t.message||"-"}
						</div>
						<div className="alert-item-time">
							${Ue(t.occurred_at)}
						</div>
					</div>
				`})}
		</div>
	`:O`<${At}
			title="最近没有异常或高优先级告警"
			description="当前运行状态较稳定。"
		/>`}function SO({items:e}){return e?.length?O`
		<div className="list-stack">
			${e.map(t=>O`
					<div className="trend-item" key=${t.day}>
						<div>
							<div className="trend-day">${t.day}</div>
							<div className="trend-meta">
								上新 ${t.new_count||0} 条
							</div>
						</div>
						<${Fe}
							size="small"
							label=${`\u964D\u4EF7 ${t.price_drop_count||0} \u6761`}
							variant="outlined"
						/>
					</div>
				`)}
		</div>
	`:O`<${At}
			title="近 7 天没有通知趋势数据"
			description="跑出通知后这里会显示按天统计。"
		/>`}function py({title:e,preview:t}){return t?O`
		<${ze}
			title=${e}
			description=${`${t.keyword} \xB7 \u6293\u53D6 ${t.page_count} \u9875`}
			className="query-preview-card"
		>
			<${Ee} spacing=${2.5}>
				<div className="summary-panel">
					<div className="summary-panel-title">分析摘要</div>
					<div className="summary-panel-text">
						${t.summary||"\u6682\u65E0\u6458\u8981"}
					</div>
					<div className="chip-row">
						<${Fe}
							size="small"
							label=${t.used_llm?"LLM \u63A8\u8350":"\u89C4\u5219\u63A8\u8350"}
							color="primary"
						/>
						<${Fe}
							size="small"
							label=${`\u539F\u59CB ${t.raw_total||0}`}
							variant="outlined"
						/>
						<${Fe}
							size="small"
							label=${`\u521D\u7B5B ${t.filtered_total||0}`}
							variant="outlined"
						/>
						<${Fe}
							size="small"
							label=${t.filter_mode||"-"}
							variant="outlined"
						/>
					</div>
				</div>

				${t.fallback_reason?O`<${Ur} severity="warning" variant="outlined"
							>${t.fallback_reason}<//
						>`:null}
				${t.items?.length?O`
							<div className="result-grid">
								${t.items.map(r=>{let o=RO(r.risk),n=r.deep_analysis||null,s=n?.image_urls?.[0]||"";return O`
										<div
											className="result-card"
											key=${r.item_id}
										>
											${s?O`<img
														className="result-card-image"
														src=${s}
														alt=${r.title}
														loading="lazy"
													/>`:null}
											<div className="result-card-head">
												<div
													className="result-card-title"
												>
													${r.title}
												</div>
												<${Fe}
													size="small"
													label=${PO(r.score)}
													color="primary"
												/>
											</div>
											<div className="result-card-price">
												${qe(r.price)}
											</div>
											<div className="result-card-reason">
												${r.reason||"\u6682\u65E0\u63A8\u8350\u7406\u7531"}
											</div>
											<div className="chip-row">
												<${Fe}
													size="small"
													label=${o.label}
													color=${o.color}
													variant=${o.variant}
												/>
												${n?O`<${Fe}
															size="small"
															label=${`\u4FE1\u7528 ${n.credit_status||"unknown"}`}
															color=${n.credit_status==="good"?"success":n.credit_status==="bad"?"error":"default"}
															variant="outlined"
														/>`:null}
											</div>
											${n?O`
														<div className="deep-analysis-box">
															<div>
																卖家信用：${n.credit_reason||n.credit_status||"-"}
															</div>
															<div>
																深度分析：${n.summary||"\u6682\u65E0\u6458\u8981"}
															</div>
															${n.want_count!=null||n.browse_count!=null?O`<div>
																		热度：${n.want_count!=null?`\u60F3\u8981 ${n.want_count}`:""}
																		${n.browse_count!=null?` \u6D4F\u89C8 ${n.browse_count}`:""}
																	</div>`:null}
														</div>
													`:null}
											<${pe}
												variant="outlined"
												href=${r.url}
												target="_blank"
											>
												打开商品页
											<//>
										</div>
									`})}
							</div>
						`:O`<${At}
							title="本次没有命中推荐商品"
							description="可以尝试放宽关键词或增加抓取页数。"
						/>`}
			<//>
		<//>
	`:null}function kO({loading:e,error:t,onLogin:r}){let[o,n]=(0,Q.useState)("");return O`
		<${Ce} className="login-shell">
			<${Tl} className="login-card" elevation=${0}>
				<${bl} sx=${{p:{xs:3,md:4}}}>
					<${Ee} spacing=${3}>
						<div className="brand-row">
							<div className="brand-mark brand-mark-large">
								<img
									src="./logo.png"
									alt="Goofish Catcher logo"
									className="brand-mark-img"
								/>
							</div>
							<div>
								<${ie} variant="h5">闲鱼监控管理后台<//>
								<${ie}
									variant="body2"
									color="text.secondary"
									sx=${{mt:.75}}
								>
									使用管理员 API Key 登录本地控制台。
								<//>
							</div>
						</div>
						${t?O`<${Ur} severity="error" variant="filled"
									>${t}<//
								>`:null}
						<${mr}
							label="管理员 API Key"
							type="password"
							value=${o}
							onChange=${s=>n(s.target.value)}
							onKeyDown=${s=>{s.key==="Enter"&&o.trim()&&r(o.trim())}}
							hint="输入后台配置的 API Key"
						/>
						<${pe}
							variant="contained"
							size="large"
							disabled=${e||!o.trim()}
							onClick=${()=>r(o.trim())}
						>
							${e?"\u767B\u5F55\u4E2D...":"\u8FDB\u5165\u540E\u53F0"}
						<//>
					<//>
				<//>
			<//>
		<//>
	`}function OO({open:e,title:t="\u786E\u8BA4\u64CD\u4F5C",description:r="",confirmText:o="\u786E\u8BA4",cancelText:n="\u53D6\u6D88",destructive:s=!1,onCancel:i,onConfirm:a}){return O`
		<${Fn}
			open=${e}
			onClose=${i}
			fullWidth=${!0}
			maxWidth="xs"
		>
			<${Wn}>${t}<//>
			${r?O`
						<${Un}>
							<${ie} variant="body2" color="text.secondary">
								${r}
							<//>
						<//>
					`:null}
			<${Li} sx=${{px:3,pb:3,pt:2}}>
				<${pe} onClick=${i}>${n}<//>
				<${pe}
					variant="contained"
					color=${s?"error":"primary"}
					onClick=${a}
				>
					${o}
				<//>
			<//>
		<//>
	`}function NO({open:e,value:t,onClose:r,onSubmit:o}){let[n,s]=(0,Q.useState)(t||{});(0,Q.useEffect)(()=>{s(t||{})},[e,t]);let i=[["umo","\u4F1A\u8BDD\u6765\u6E90 UMO","text","\u7528\u4E8E\u6807\u8BC6\u6D88\u606F\u4F1A\u8BDD\u6216\u901A\u77E5\u51FA\u53E3"],["keyword","\u5173\u952E\u8BCD","text","\u8BA2\u9605\u5173\u952E\u8BCD\uFF0C\u5FC5\u987B\u586B\u5199"],["interval_sec","\u8F6E\u8BE2\u95F4\u9694\uFF08\u79D2\uFF09","number","\u5EFA\u8BAE\u4E0D\u8981\u4F4E\u4E8E 300 \u79D2"],["pages","\u6293\u53D6\u9875\u6570","number","\u5EFA\u8BAE 1-2 \u9875"],["recommend_max_price","\u63A8\u8350\u6700\u9AD8\u4EF7","number","\u53EA\u63A8\u8350\u4EF7\u683C\u4E0D\u9AD8\u4E8E\u8BE5\u503C\u7684\u5546\u54C1\uFF1B\u7559\u7A7A\u8868\u793A\u4E0D\u8FC7\u6EE4"],["drop_abs","\u7EDD\u5BF9\u964D\u4EF7\u9608\u503C","number","\u5355\u4F4D\uFF1A\u5143"],["drop_pct","\u76F8\u5BF9\u964D\u4EF7\u9608\u503C","number","\u4F8B\u5982 0.05 \u8868\u793A 5%"],["new_window_sec","\u4E0A\u65B0\u7A97\u53E3\uFF08\u79D2\uFF09","number","\u7528\u4E8E\u5224\u5B9A\u4E0A\u65B0\u65F6\u95F4\u7A97"],["cooldown_sec","\u901A\u77E5\u51B7\u5374\uFF08\u79D2\uFF09","number","\u76F8\u540C\u5546\u54C1\u4E8B\u4EF6\u7684\u901A\u77E5\u95F4\u9694"],["price_min","\u6700\u4F4E\u4EF7\uFF08\u5143\uFF09","number","0 \u6216\u7559\u7A7A\u8868\u793A\u4E0D\u9650"],["price_max","\u6700\u9AD8\u4EF7\uFF08\u5143\uFF09","number","0 \u6216\u7559\u7A7A\u8868\u793A\u4E0D\u9650"]];return O`
		<${Fn}
			open=${e}
			onClose=${r}
			fullWidth=${!0}
			maxWidth="md"
		>
			<${Wn}>${t?.id?"\u7F16\u8F91\u8BA2\u9605":"\u65B0\u5EFA\u8BA2\u9605"}<//>
			<${Un} dividers=${!0}>
				<div className="form-grid">
					${i.map(([a,l,p,c])=>O`
							<${mr}
								key=${a}
								label=${l}
								type=${p}
								value=${n[a]??""}
								hint=${c}
								onChange=${u=>s(f=>({...f,[a]:u.target.value}))}
							/>
						`)}
				</div>
				<${Ce} sx=${{mt:2.5}}>
					<${ie} variant="subtitle2" sx=${{mb:1.5}}>
						高级筛选
					<//>
					<div className="form-grid">
						<${Ce} className="field-block">
							<div className="field-label">个人闲置</div>
							<${Ee}
								direction="row"
								alignItems="center"
								spacing=${1.5}
								sx=${{minHeight:44}}
							>
								<${yn}
									checked=${!!n.personal_only}
									onChange=${a=>s(l=>({...l,personal_only:a.target.checked}))}
								/>
								<${ie} variant="body2" color="text.secondary">
									只看个人闲置商品
								<//>
							<//>
							<div className="field-hint">默认关闭，不影响旧订阅</div>
						<//>
						<${Ce} className="field-block">
							<div className="field-label">包邮</div>
							<${Ee}
								direction="row"
								alignItems="center"
								spacing=${1.5}
								sx=${{minHeight:44}}
							>
								<${yn}
									checked=${!!n.free_shipping}
									onChange=${a=>s(l=>({...l,free_shipping:a.target.checked}))}
								/>
								<${ie} variant="body2" color="text.secondary">
									只看包邮商品
								<//>
							<//>
							<div className="field-hint">默认关闭</div>
						<//>
						<${mr}
							label="新发布范围"
							value=${n.new_publish_option??""}
							onChange=${a=>s(l=>({...l,new_publish_option:a.target.value}))}
							hint="如 24小时内 / 7天内 / 14天内，留空不限"
						/>
						<${mr}
							label="地区"
							value=${n.region??""}
							onChange=${a=>s(l=>({...l,region:a.target.value}))}
							hint="格式如 江苏/南京/全南京，留空不限"
						/>
					</div>
				<//>
			<//>
			<${Li} sx=${{px:3,pb:3,pt:2}}>
				<${pe} onClick=${r}>取消<//>
				<${pe} variant="contained" onClick=${()=>o(n)}
					>保存<//
				>
			<//>
		<//>
	`}function HT({notify:e,temporaryQuery:t,onTemporaryQueryChange:r,onRunTemporaryQuery:o}){let[n,s]=(0,Q.useState)(null),[i,a]=(0,Q.useState)(!0);async function l(){try{let u=await Me("/api/overview");(0,Q.startTransition)(()=>s(u))}catch(u){e(u.message,"error")}finally{a(!1)}}if((0,Q.useEffect)(()=>{l();let u=window.setInterval(l,8e3);return()=>window.clearInterval(u)},[]),i&&!n)return O`
			<${Ce} sx=${{display:"grid",placeItems:"center",py:12}}>
				<${Wr} />
			<//>
		`;let p=n?.provider_health||{},c=[{label:"\u6293\u53D6\u6A21\u5F0F",value:n?.provider_mode||"-"},{label:"Provider \u72B6\u6001",value:n?.provider_available?"\u53EF\u7528":"\u5F02\u5E38"},{label:"\u8C03\u5EA6\u5668",value:n?.scheduler_running?"\u8FD0\u884C\u4E2D":"\u672A\u8FD0\u884C"},{label:"\u6700\u8FD1\u68C0\u67E5",value:Ue(n?.provider_health_checked_at)},{label:"\u8BA4\u8BC1\u72B6\u6001",value:p.auth||"-"},{label:"\u767B\u5F55\u6001\u6587\u4EF6",value:p.storage_state===void 0||p.storage_state===null?"-":p.storage_state?"\u5DF2\u5C31\u7EEA":"\u672A\u627E\u5230"}];return O`
		<${Ee} spacing=${Lt.pageGap} className="page-enter page-stack">
			<${tn}
				title="控制台总览"
				description="保留运行决策最需要看的状态、告警和快速查询。"
			/>

			<div className="stats-grid">
				<${vn}
					label="订阅数量"
					value=${`${n?.enabled_subscriptions||0} / ${n?.total_subscriptions||0}`}
					hint=${`\u542F\u7528 ${n?.enabled_subscriptions||0}\uFF0C\u6682\u505C ${n?.paused_subscriptions||0}`}
					tone="primary"
				/>
				<${vn}
					label="24 小时成功率"
					value=${`${Number(n?.success_rate_24h||0).toFixed(1)}%`}
					hint=${`\u6210\u529F ${n?.success_runs_24h||0} \u6B21\uFF0C\u5931\u8D25 ${n?.failed_runs_24h||0} \u6B21`}
					tone="success"
				/>
				<${vn}
					label="队列 / 执行中"
					value=${`${n?.queue_size||0} / ${n?.inflight||0}`}
					hint=${`Worker \u6570\u91CF ${n?.workers||0}`}
					tone="secondary"
				/>
				<${vn}
					label="最近告警"
					value=${n?.recent_alerts?.length||0}
					hint="展示最近业务与运行异常"
					tone="warning"
				/>
			</div>

			<div className="content-grid two-column">
				<${Ee} spacing=${Lt.pageGap}>
					<${ze}
						title="临时查询"
						description="不创建订阅，直接执行一次推荐分析。"
					>
						<div className="filter-grid">
							<${mr}
								label="关键词"
								value=${t.keyword}
								onChange=${u=>r({keyword:u.target.value})}
								hint="输入你想临时分析的关键词"
							/>
							<${mr}
								label="页数"
								type="number"
								value=${t.pages}
								onChange=${u=>r({pages:u.target.value})}
								wrapperSx=${{width:{xs:"100%",md:120}}}
							/>
							<${mr}
								label="最低价"
								type="number"
								value=${t.price_min??""}
								onChange=${u=>r({price_min:u.target.value})}
								wrapperSx=${{width:{xs:"100%",md:120}}}
							/>
							<${mr}
								label="最高价"
								type="number"
								value=${t.price_max??""}
								onChange=${u=>r({price_max:u.target.value})}
								wrapperSx=${{width:{xs:"100%",md:120}}}
							/>
							<${mr}
								label="新发布范围"
								value=${t.new_publish_option??""}
								onChange=${u=>r({new_publish_option:u.target.value})}
								hint="如 24小时内 / 7天内"
							/>
							<${mr}
								label="地区"
								value=${t.region??""}
								onChange=${u=>r({region:u.target.value})}
								hint="如 江苏/南京/全南京"
							/>
							<${Ce} className="field-block">
								<div className="field-label">个人闲置</div>
								<${Ee}
									direction="row"
									alignItems="center"
									spacing=${1}
									sx=${{minHeight:44}}
								>
									<${yn}
										checked=${!!t.personal_only}
										onChange=${u=>r({personal_only:u.target.checked})}
									/>
									<${ie} variant="body2" color="text.secondary">
										仅个人闲置
									<//>
								<//>
							<//>
							<${Ce} className="field-block">
								<div className="field-label">包邮</div>
								<${Ee}
									direction="row"
									alignItems="center"
									spacing=${1}
									sx=${{minHeight:44}}
								>
									<${yn}
										checked=${!!t.free_shipping}
										onChange=${u=>r({free_shipping:u.target.checked})}
									/>
									<${ie} variant="body2" color="text.secondary">
										仅包邮
									<//>
								<//>
							<//>
							<${pe}
								variant="contained"
								onClick=${o}
								disabled=${t.loading||!t.keyword.trim()}
								startIcon=${t.loading?O`<${Wr}
											size=${16}
											color="inherit"
										/>`:null}
							>
								${t.loading?"\u5206\u6790\u4E2D...":"\u5F00\u59CB\u5206\u6790"}
							<//>
						</div>

						${t.preview?O`<${Ce} sx=${{mt:3}}
									><${py}
										title="查询结果"
										preview=${t.preview}
								/><//>`:null}
					<//>
				<//>
				<${Ee} spacing=${Lt.pageGap}>
					<${ze}
						title="运行状态"
						description="当前 Provider 与调度器的核心状态。"
					>
						${n?.provider_error?O`<${Ur}
									severity="error"
									variant="outlined"
									sx=${{mb:2}}
								>
									${n.provider_error}
								<//>`:null}
						<${ra} items=${c} />
					<//>
					<${ze}
						title="最近告警"
						description="帮助快速确认当前是否需要手动介入。"
					>
						<${EO} items=${n?.recent_alerts||[]} />
					<//>
					<${ze}
						title="近 7 天趋势"
						description="按天查看上新与降价通知数量。"
					>
						<${SO} items=${n?.trends||[]} />
					<//>
				<//>
			</div>
		<//>
	`}function KT({notify:e}){let[t,r]=(0,Q.useState)({keyword:"",status:"all"}),[o,n]=(0,Q.useState)([]),[s,i]=(0,Q.useState)(0),[a,l]=(0,Q.useState)(!0),[p,c]=(0,Q.useState)(!1),[u,f]=(0,Q.useState)(null),[v,x]=(0,Q.useState)(null),[h,b]=(0,Q.useState)(null),[y,m]=(0,Q.useState)(null),g=(0,Q.useDeferredValue)(t.keyword);async function T(){try{let _=new URLSearchParams({keyword:g,status:t.status}),S=await Me(`/api/subscriptions?${_.toString()}`);(0,Q.startTransition)(()=>{n(S.items||[]),i(S.total||0)})}catch(_){e(_.message,"error")}finally{l(!1)}}(0,Q.useEffect)(()=>{l(!0),T()},[g,t.status]);async function w(_){let S={..._,interval_sec:gn(_.interval_sec),pages:gn(_.pages),recommend_max_price:gn(_.recommend_max_price),drop_abs:gn(_.drop_abs),drop_pct:gn(_.drop_pct),new_window_sec:gn(_.new_window_sec),cooldown_sec:gn(_.cooldown_sec),price_min:gn(_.price_min),price_max:gn(_.price_max),personal_only:!!_.personal_only,free_shipping:!!_.free_shipping,new_publish_option:String(_.new_publish_option||"").trim(),region:String(_.region||"").trim()};try{u?.id?await Me(`/api/subscriptions/${u.id}`,{method:"PATCH",body:S}):await Me("/api/subscriptions",{method:"POST",body:S}),e("\u8BA2\u9605\u5DF2\u4FDD\u5B58","success"),c(!1),f(null),T()}catch(R){e(R.message,"error")}}async function $(_,S){try{let R=await Me(`/api/subscriptions/${_}/${S}`,{method:"POST"});S==="check"&&(0,Q.startTransition)(()=>x(R.recommendation)),e("\u64CD\u4F5C\u6210\u529F","success"),T()}catch(R){e(R.message,"error")}}async function C(_){try{await Me(`/api/subscriptions/${_}`,{method:"DELETE"}),e("\u8BA2\u9605\u5DF2\u5220\u9664","success"),T()}catch(S){e(S.message,"error")}}return O`
		<${Ee} spacing=${Lt.pageGap} className="page-enter page-stack">
			<${tn}
				title="订阅管理"
				description="统一管理关键词、轮询频率和事件阈值。"
				action=${O`
					<${pe}
						variant="contained"
						onClick=${()=>{f({interval_sec:600,pages:1,recommend_max_price:"",drop_abs:50,drop_pct:.05,new_window_sec:1800,cooldown_sec:21600,personal_only:!1,free_shipping:!1,new_publish_option:"",region:""}),c(!0)}}
					>
						新建订阅
					<//>
				`}
			/>

			<${ze}
				title="筛选"
				description=${`\u5F53\u524D\u5171 ${s} \u6761\u8BA2\u9605`}
			>
				<div className="filter-grid">
					<${mr}
						label="关键词"
						value=${t.keyword}
						onChange=${_=>r(S=>({...S,keyword:_.target.value}))}
					/>
					<${mr}
						select=${!0}
						label="状态"
						value=${t.status}
						onChange=${_=>r(S=>({...S,status:_.target.value}))}
						wrapperSx=${{width:{xs:"100%",md:160}}}
					>
						<${dt} value="all">全部<//>
						<${dt} value="enabled">启用<//>
						<${dt} value="paused">暂停<//>
					<//>
				</div>
			<//>

			<${ze}
				title="订阅列表"
				description="只保留操作所需的关键信息。"
			>
				${a?O`<${Xo} sx=${{mb:2}} />`:null}
				${o.length?O`
							<${Er}
								className="table-wrap relaxed-table managed-table"
							>
								<${_r} size="small">
									<${Sr}>
										<${nt}>
											<${X} className="table-primary-cell"
												>关键词<//>
											<${X}>状态<//>
											<${X}>频率<//>
											<${X}>规则<//>
											<${X}>最近执行<//>
											<${X}>失败<//>
											<${X}
												align="right"
												className="table-action-cell"
											>
												操作
											<//>
										<//>
									<//>
									<${Rr}>
										${o.map(_=>{let S=Kl(_.enabled,_.paused_reason),R=$W(_);return O`
												<${nt}
													key=${_.id}
													hover=${!0}
												>
													<${X}
														className="table-primary-cell"
													>
														<div className="table-primary-copy">
															<${ie}
																variant="subtitle2"
																className="table-primary-title"
																>${_.keyword}<//
															>
															<${ie}
																variant="caption"
																color="text.secondary"
																className="table-primary-meta"
															>
																${`#${_.id} \xB7 UMO ${_.umo}`}
															<//>
														</div>
													<//>
													<${X}>
														<${Fe}
															size="small"
															label=${S.label}
															color=${S.color}
															variant=${S.variant}
														/>
													<//>
													<${X}>
														<${ie}
															variant="body2"
															>${ql(_.interval_sec)}<//
														>
														<${ie}
															variant="caption"
															color="text.secondary"
														>
															${_.pages} 页
														<//>
													<//>
													<${X}>
														<${ie}
															variant="body2"
														>
															推荐价
															${_.recommend_max_price==null?"\u4E0D\u9650":`\u2264${qe(_.recommend_max_price)}`}
														<//>
														<${ie}
															variant="caption"
															color="text.secondary"
														>
															降价
															${qe(_.drop_abs)}
															/
															${bO(_.drop_pct)}
														<//>
														<${ie}
															variant="caption"
															color="text.secondary"
														>
															上新
															${ql(_.new_window_sec)}，冷却
															${ql(_.cooldown_sec)}
														<//>
														${R.length?O`<div className="chip-row tiny-chip-row">
																	${R.map(j=>O`
																			<${Fe}
																				key=${j}
																				size="small"
																				label=${j}
																				variant="outlined"
																			/>
																		`)}
																</div>`:O`<${ie}
																	variant="caption"
																	color="text.secondary"
																>
																	高级筛选未开启
																<//>`}
													<//>
													<${X}>
														<${ie}
															variant="body2"
															>${Ue(_.last_run_at)}<//
														>
														<${ie}
															variant="caption"
															color="text.secondary"
														>
															下次
															${Ue(_.next_run_at)}
														<//>
													<//>
													<${X}
														>${_.consecutive_failures}<//
													>
													<${X}
														align="right"
														className="table-action-cell"
													>
														<div
															className="table-actions"
														>
															<${pe}
																size="small"
																onClick=${()=>{f(_),c(!0)}}
															>
																编辑
															<//>
															<${pe}
																size="small"
																onClick=${()=>b(_)}
															>
																统计
															<//>
															<${pe}
																size="small"
																onClick=${()=>$(_.id,"check")}
															>
																立即检查
															<//>
															<${pe}
																size="small"
																onClick=${()=>$(_.id,_.enabled?"pause":"resume")}
															>
																${_.enabled?"\u6682\u505C":"\u6062\u590D"}
															<//>
															<${pe}
																size="small"
																color="error"
																onClick=${()=>m(_)}
															>
																删除
															<//>
														</div>
													<//>
												<//>
											`})}
									<//>
								<//>
							<//>
						`:O`<${At}
							title="没有匹配的订阅"
							description="试试调整筛选条件，或直接新建一条订阅。"
						/>`}
			<//>

			${v?O`<${py}
						title="最近一次检查"
						preview=${v}
					/>`:null}

			<${NO}
				open=${p}
				value=${u}
				onClose=${()=>{c(!1),f(null)}}
				onSubmit=${w}
			/>
			<${wW}
				open=${!!h}
				subscription=${h}
				onClose=${()=>b(null)}
				notify=${e}
			/>
			<${OO}
				open=${!!y}
				title="删除订阅"
				description=${y?`\u786E\u8BA4\u5220\u9664\u300C${y.keyword}\u300D\u8FD9\u6761\u8BA2\u9605\uFF1F\u5220\u9664\u540E\u4E0D\u53EF\u6062\u590D\uFF0C\u5DF2\u6293\u53D6\u7684\u5546\u54C1\u8BB0\u5F55\u4ECD\u4FDD\u7559\u5728\u6570\u636E\u5E93\u4E2D\u3002`:""}
				confirmText="删除"
				destructive=${!0}
				onCancel=${()=>m(null)}
				onConfirm=${()=>{let _=y;m(null),_&&C(_.id)}}
			/>
		<//>
	`}function $W(e){let t=[];if(e.price_min!=null||e.price_max!=null){let r=[];e.price_min!=null&&r.push(`\u2265${qe(e.price_min)}`),e.price_max!=null&&r.push(`\u2264${qe(e.price_max)}`),t.push(`\u4EF7\u683C ${r.join(" ")}`)}return e.personal_only&&t.push("\u4E2A\u4EBA\u95F2\u7F6E"),e.free_shipping&&t.push("\u5305\u90AE"),e.new_publish_option&&t.push(`\u65B0\u53D1\u5E03 ${e.new_publish_option}`),e.region&&t.push(`\u5730\u533A ${e.region}`),t}function wW({open:e,subscription:t,onClose:r,notify:o}){let[n,s]=(0,Q.useState)(null),[i,a]=(0,Q.useState)(!1);(0,Q.useEffect)(()=>{if(!e||!t?.id){s(null);return}let u=!1;async function f(){a(!0);try{let v=await Me(`/api/subscriptions/${t.id}/analytics`);u||s(v)}catch(v){u||o(v.message,"error")}finally{u||a(!1)}}return f(),()=>{u=!0}},[e,t?.id]);let l=n?.stats||{},p=n?.notification_trends||[],c=n?.recent_recommendations||[];return O`
		<${Fn} open=${e} onClose=${r} fullWidth=${!0} maxWidth="lg">
			<${Wn}>
				${t?`\u8BA2\u9605\u7EDF\u8BA1\uFF1A${t.keyword}`:"\u8BA2\u9605\u7EDF\u8BA1"}
			<//>
			<${Un} dividers=${!0}>
				${i&&!n?O`<${Ce} sx=${{display:"grid",placeItems:"center",py:8}}>
							<${Wr} />
						<//>`:O`
							<${Ee} spacing=${3}>
								<div className="stats-grid compact-stats-grid">
									<${tu} label="样本数" value=${l.sample_count??0} />
									<${tu} label="均价" value=${qe(l.avg_price)} />
									<${tu} label="中位数" value=${qe(l.median_price)} />
									<${tu} label="最低价" value=${qe(l.min_price)} />
									<${tu} label="最高价" value=${qe(l.max_price)} />
								</div>
								<${ze}
									title="历史价格走势"
									description="基于 price_history 的轻量 SVG 折线图。"
								>
									<${RW}
										points=${n?.price_series||[]}
										valueKey="price"
									/>
								<//>
								<${ze}
									title="近 30 天通知趋势"
									description="上新与降价通知按天聚合。"
								>
									<${kW} trends=${p} />
								<//>
								<${ze} title="最近推荐商品">
									${c.length?O`<${Er} className="table-wrap compact-table">
												<${_r} size="small">
													<${Sr}>
														<${nt}>
															<${X}>时间<//>
															<${X}>事件<//>
															<${X}>商品<//>
															<${X}>价格<//>
														<//>
													<//>
													<${Rr}>
														${c.map(u=>O`
															<${nt} key=${`${u.item_id}-${u.sent_at}`}>
																<${X}>${Ue(u.sent_at)}<//>
																<${X}>${u.event_type}<//>
																<${X}>
																	<${pe}
																		href=${u.url}
																		target="_blank"
																		size="small"
																	>
																		${u.title||u.item_id}
																	<//>
																<//>
																<${X}>${qe(u.price)}<//>
															<//>
														`)}
													<//>
												<//>
											<//>`:O`<${At}
												title="暂无推荐记录"
												description="发送推荐后这里会展示最近商品。"
											/>`}
								<//>
							<//>
						`}
			<//>
		<//>
	`}function tu({label:e,value:t}){return O`
		<div className="stat-mini">
			<div className="stat-mini-label">${e}</div>
			<div className="stat-mini-value">${t}</div>
		</div>
	`}function _W(e){let t=e.length,r=e[Math.floor(t/4)],o=e[Math.floor(t*3/4)],n=o-r,s=e[Math.floor(t/2)];return n>0?{lo:r-1.5*n,hi:o+1.5*n}:s>0?{lo:s*.1,hi:s*10}:null}function RW({points:e,valueKey:t}){let o=EW(e||[],t),n=o.flatMap(E=>[E.avg,E.median,E.min,E.max]);if(!n.length)return O`<${At}
			title="暂无价格样本"
			description="订阅产生价格历史后会显示走势。"
		/>`;let s=760,i=260,a=72,l=20,p=18,c=34,u=s-a-l,f=i-p-c,v=[...n].sort((E,F)=>E-F),x=_W(v),h=x?Math.max(v[0],x.lo):v[0],b=x?Math.min(v[v.length-1],x.hi):v[v.length-1],y=b-h||1,m=E=>o.length===1?a+u/2:a+u/(o.length-1)*E,g=E=>{let F=Math.min(Math.max(E,h),b);return p+(1-(F-h)/y)*f},T=E=>o.map((F,ae)=>`${ae===0?"M":"L"}${m(ae).toFixed(1)},${g(F[E]).toFixed(1)}`).join(" "),w=()=>{if(!o.length)return"";let E=o.map((ae,ye)=>`${ye===0?"M":"L"}${m(ye).toFixed(1)},${g(ae.max).toFixed(1)}`).join(" "),F=[...o].reverse().map((ae,ye)=>{let me=o.length-1-ye;return`L${m(me).toFixed(1)},${g(ae.min).toFixed(1)}`}).join(" ");return`${E} ${F} Z`},$=T("avg"),C=T("median"),_=w(),S=m(0),R=m(o.length-1),j=p+f,U=$?`${$} L${R.toFixed(1)},${j.toFixed(1)} L${S.toFixed(1)},${j.toFixed(1)} Z`:"",z=Array.from({length:5},(E,F)=>{let ae=F/4,ye=h+ae*y;return{y:p+(1-ae)*f,label:qT(ye)}}),Z=Math.min(5,o.length),B=Array.from({length:Z},(E,F)=>{let ae=Math.round(F/(Z-1||1)*(o.length-1));return{x:m(ae),label:o[ae]?.label||""}}),D=o[o.length-1],q=o.reduce((E,F)=>E+F.count,0);return O`
		<div className="chart-shell enhanced-chart-shell">
			<div className="chart-legend-row">
				<div className="chart-legend-group">
					<span className="chart-legend-item avg"><span></span>每日均价</span>
					<span className="chart-legend-item median"><span></span>每日中位数</span>
					<span className="chart-legend-item range"><span></span>最低/最高区间</span>
				</div>
				<div className="chart-legend-meta">
					${o.length} 天 · ${q} 个价格样本
				</div>
			</div>
			<svg viewBox=${`0 0 ${s} ${i}`} className="analytics-svg enhanced-analytics-svg" role="img" aria-label="历史价格趋势">
				<defs>
					<linearGradient id="goofish-price-area-fill" x1="0%" y1="0%" x2="0%" y2="100%">
						<stop offset="0%" stopColor="var(--primary)" stopOpacity="0.28" />
						<stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
					</linearGradient>
					<linearGradient id="goofish-price-range-fill" x1="0%" y1="0%" x2="0%" y2="100%">
						<stop offset="0%" stopColor="var(--warning)" stopOpacity="0.16" />
						<stop offset="100%" stopColor="var(--warning)" stopOpacity="0.05" />
					</linearGradient>
				</defs>

				${z.map(({y:E,label:F})=>O`
					<line
						x1=${a} y1=${E.toFixed(1)}
						x2=${s-l} y2=${E.toFixed(1)}
						stroke="var(--border-soft)" strokeWidth="1" strokeDasharray="4 6"
					/>
					<text
						x=${a-8} y=${E.toFixed(1)}
						textAnchor="end" dominantBaseline="middle"
						fill="var(--muted)" fontSize="11"
					>${F}</text>
				`)}

				<line x1=${a} y1=${p} x2=${a} y2=${j} stroke="var(--border-soft)" strokeWidth="1" />
				<line x1=${a} y1=${j} x2=${s-l} y2=${j} stroke="var(--border-soft)" strokeWidth="1" />
				<path d=${_} fill="url(#goofish-price-range-fill)" />
				<path d=${U} fill="url(#goofish-price-area-fill)" />
				<path d=${$} fill="none" stroke="var(--primary)" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
				<path d=${C} fill="none" stroke="var(--warning)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="8 7" />

				${o.map((E,F)=>O`
					<g key=${E.day}>
						<circle cx=${m(F).toFixed(1)} cy=${g(E.avg).toFixed(1)} r="4.5" fill="var(--primary)">
							<title>${`${E.day} \u5747\u4EF7 ${qe(E.avg)}\uFF0C\u4E2D\u4F4D\u6570 ${qe(E.median)}\uFF0C\u6837\u672C ${E.count}`}</title>
						</circle>
						<circle cx=${m(F).toFixed(1)} cy=${g(E.median).toFixed(1)} r="3.5" fill="var(--warning)">
							<title>${`${E.day} \u4E2D\u4F4D\u6570 ${qe(E.median)}`}</title>
						</circle>
					</g>
				`)}
				${B.map(({x:E,label:F})=>F&&O`
					<text
						x=${E.toFixed(1)} y=${i-10}
						textAnchor="middle"
						fill="var(--muted)" fontSize="11"
					>${F}</text>
				`)}
				<line
					x1=${R.toFixed(1)} y1=${p}
					x2=${R.toFixed(1)} y2=${j}
					stroke="var(--primary)" strokeWidth="1.2" strokeDasharray="3 7"
					opacity="0.55"
				/>
				<circle cx=${R.toFixed(1)} cy=${g(D.avg).toFixed(1)} r="7" fill="none" stroke="var(--primary)" strokeWidth="2" opacity="0.72" />
			</svg>
			<div className="chart-meta chart-meta-grid">
				<span>展示范围 ${qT(h)} ~ ${qT(b)}</span>
				<span>最新 ${D?.label||"-"}：均价 ${qe(D?.avg)} / 中位数 ${qe(D?.median)} / 区间 ${qe(D?.min)}~${qe(D?.max)}</span>
			</div>
		</div>
	`}function EW(e,t){let r=new Map;for(let o of e||[]){let n=Number(o?.[t]);if(!Number.isFinite(n))continue;let s=Number(o?.observed_at||0),i=s?new Date(s*1e3).toLocaleDateString("zh-CN",{year:"numeric",month:"2-digit",day:"2-digit"}):"\u672A\u77E5\u65E5\u671F";r.has(i)||r.set(i,[]),r.get(i).push(n)}return Array.from(r.entries()).map(([o,n])=>{let s=[...n].sort((a,l)=>a-l),i=s.reduce((a,l)=>a+l,0)/s.length;return{day:o,label:o.replace(/^\d{4}\//,""),count:s.length,avg:MO(i),median:MO(SW(s)),min:s[0],max:s[s.length-1]}})}function SW(e){if(!e.length)return 0;let t=Math.floor(e.length/2);return e.length%2===0?(e[t-1]+e[t])/2:e[t]}function MO(e){return Math.round(Number(e||0)*100)/100}function qT(e){let t=Number(e);return Number.isFinite(t)?Math.abs(t)>=1e4?`\xA5${(t/1e4).toFixed(1)}\u4E07`:`\xA5${Math.round(t)}`:"-"}function kW({trends:e}){let t=e||[];if(!t.length)return O`<${At}
			title="暂无通知趋势"
			description="最近 30 天没有通知记录。"
		/>`;let r=t.map(a=>({...a,newCount:Number(a.new_count||0),dropCount:Number(a.price_drop_count||0)})),o=r.reduce((a,l)=>a+l.newCount,0),n=r.reduce((a,l)=>a+l.dropCount,0),s=r.slice(-7).reduce((a,l)=>a+l.newCount+l.dropCount,0),i=Math.max(1,...r.map(a=>a.newCount+a.dropCount));return O`
		<div className="trend-bars">
			<div className="trend-summary-row">
				<div><strong>${o}</strong><span>上新通知</span></div>
				<div><strong>${n}</strong><span>降价通知</span></div>
				<div><strong>${s}</strong><span>近 7 天合计</span></div>
			</div>
			<div className="chart-legend-row compact">
				<div className="chart-legend-group">
					<span className="chart-legend-item notice-new"><span></span>上新</span>
					<span className="chart-legend-item notice-drop"><span></span>降价</span>
				</div>
				<div className="chart-legend-meta">按天堆叠展示</div>
			</div>
			${r.map(a=>{let l=a.newCount+a.dropCount;return O`
					<div className="trend-bar-row" key=${a.day}>
						<div className="trend-bar-day">${a.day}</div>
						<div className="trend-bar-track">
							<div className="trend-bar-stack">
								<div
									className="trend-bar-segment new"
									title=${`\u4E0A\u65B0 ${a.newCount}`}
									style=${{width:`${a.newCount/i*100}%`}}
								></div>
								<div
									className="trend-bar-segment drop"
									title=${`\u964D\u4EF7 ${a.dropCount}`}
									style=${{width:`${a.dropCount/i*100}%`}}
								></div>
							</div>
						</div>
						<div className="trend-bar-value">
							合计 ${l} · 上新 ${a.newCount} / 降价 ${a.dropCount}
						</div>
					</div>
				`})}
		</div>
	`}function GT({detail:e,onFocusSubscription:t,onRunSubscriptionAction:r,onDelete:o,onDeepSearch:n,deepSearchLoading:s}){let i=e?.item,a=e?.deep_analysis||null,l=a?.image_urls?.[0]||"";return O`
		${e?O`
					<${Ee} spacing=${Lt.pageGap}>
						<${Ce}>
							<${ie} variant="h5"
								>${i?.title||"-"}<//
							>
							<${ie}
								variant="body2"
								color="text.secondary"
								sx=${{mt:.75}}
							>
								${i?.item_id||"-"}
							<//>
						<//>

						<div className="chip-row">
							<${Fe}
								label=${qe(i?.price)}
								color="primary"
							/>
							<${Fe}
								label=${i?.latest_event_type||"\u65E0\u4E8B\u4EF6"}
								variant="outlined"
							/>
							<${pe}
								variant="outlined"
								href=${i?.url}
								target="_blank"
							>
								打开商品页
							<//>
							${o&&i?.item_id?O`
										<${pe}
											variant="outlined"
											color="error"
											onClick=${()=>o(i.item_id)}
										>
											删除此记录
										<//>
									`:null}
						</div>

						<${ze} title="基本信息">
							<${ra}
								items=${[{label:"\u5546\u54C1 ID",value:i?.item_id||"-"},{label:"\u53D1\u5E03\u65F6\u95F4",value:Ue(i?.publish_time)},{label:"\u9996\u6B21\u53D1\u73B0",value:Ue(i?.first_seen_at)},{label:"\u6700\u8FD1\u53D1\u73B0",value:Ue(i?.last_seen_at)},{label:"\u5173\u8054\u8BA2\u9605\u6570",value:String(i?.subscription_count||0)}]}
							/>
						<//>

						<${ze}
							title="深度分析"
							description="候选推荐前抓取的商品详情、卖家信用和风险结论。"
						>
							${a?O`
										<${Ee} spacing=${2}>
											${l?O`<img
														src=${l}
														alt=${i?.title||"\u5546\u54C1\u4E3B\u56FE"}
														className="detail-main-image"
													/>`:null}
											<div className="chip-row">
												<${Fe}
													label=${`\u4FE1\u7528 ${a.credit_status||"unknown"}`}
													color=${a.credit_status==="good"?"success":a.credit_status==="bad"?"error":"default"}
													variant="outlined"
												/>
												<${Fe}
													label=${a.status||"passed"}
													color=${a.status==="rejected"?"error":"success"}
													variant="outlined"
												/>
											</div>
											<${ra}
												items=${[{label:"\u5356\u5BB6\u4FE1\u7528",value:a.credit_reason||a.credit_status||"-"},{label:"\u63A8\u8350/\u8FC7\u6EE4\u7406\u7531",value:a.summary||"-"},{label:"\u98CE\u9669\u8BF4\u660E",value:a.risk||"-"},{label:"\u60F3\u8981\u4EBA\u6570",value:a.want_count==null?"-":String(a.want_count)},{label:"\u6D4F\u89C8\u91CF",value:a.browse_count==null?"-":String(a.browse_count)},{label:"\u5206\u6790\u65F6\u95F4",value:Ue(a.analyzed_at)},{label:"\u56FE\u7247\u94FE\u63A5",value:a.image_urls?.join("\uFF0C")||"-"}]}
											/>
										<//>
									`:O`
										<${Ee} spacing=${1.5} alignItems="flex-start">
											<${At}
												title="暂无深度分析"
												description="商品进入推荐候选后会缓存详情分析结果，也可以手动触发。"
											/>
											${n&&i?.item_id?O`
														<${pe}
															variant="contained"
															size="small"
															disabled=${s}
															onClick=${()=>n(i.item_id)}
														>
															${s?O`<${Wr} size=${16} sx=${{mr:1}} />`:null}
															触发深度搜索
														<//>
														<${ie}
															variant="caption"
															color="text.secondary"
														>
															商品详情页容易触发闲鱼滑块验证，触发后本次深度搜索会直接失败，不会自动完成验证，可稍后重试。
														<//>
													`:null}
										<//>
									`}
						<//>

						<${ze}
							title="关联订阅"
							description="在商品上下文里直接筛选、检查或暂停关联订阅。"
						>
							${e.subscriptions?.length?O`
										<${Er}
											className="table-wrap compact-table managed-table"
										>
											<${_r} size="small">
												<${Sr}>
													<${nt}>
														<${X}
															className="table-primary-cell"
														>
															关键词
														<//>
														<${X}>状态<//>
														<${X}>最后价格<//>
														<${X}>最后关联时间<//>
														<${X}
															align="right"
															className="table-action-cell"
														>
															操作
														<//>
													<//>
												<//>
												<${Rr}>
													${e.subscriptions.map(p=>{let c=Kl(p.enabled,p.paused_reason);return O`
															<${nt}
																key=${p.sub_id}
																hover=${!0}
															>
																<${X}
																	className="table-primary-cell"
																>
																	<div className="table-primary-copy">
																		<${ie}
																			variant="subtitle2"
																			className="table-primary-title"
																		>
																			${p.keyword}
																		<//>
																		<${ie}
																			variant="caption"
																			color="text.secondary"
																			className="table-primary-meta"
																		>
																			${`#${p.sub_id} \xB7 UMO ${p.umo}`}
																		<//>
																	</div>
																<//>
																<${X}>
																	<${Fe}
																		size="small"
																		label=${c.label}
																		color=${c.color}
																		variant=${c.variant}
																	/>
																<//>
																<${X}
																	>${qe(p.last_price)}<//
																>
																<${X}
																	>${Ue(p.last_seen_at)}<//
																>
																<${X}
																	align="right"
																	className="table-action-cell"
																>
																	<div className="table-actions">
																		<${pe}
																			size="small"
																			onClick=${()=>t(p.sub_id)}
																		>
																			按此查看
																		<//>
																		<${pe}
																			size="small"
																			onClick=${()=>r(p.sub_id,"check",i?.item_id||"")}
																		>
																			检查
																		<//>
																		<${pe}
																			size="small"
																			onClick=${()=>r(p.sub_id,p.enabled?"pause":"resume",i?.item_id||"")}
																		>
																			${p.enabled?"\u6682\u505C":"\u6062\u590D"}
																		<//>
																	</div>
																<//>
															<//>
														`})}
												<//>
											<//>
										<//>
									`:O`<${At}
										title="没有关联订阅"
										description="这个商品还没有命中过任何订阅条目。"
									/>`}
						<//>

						<${ze}
							title="价格历史"
							description="默认展示最近 20 条价格记录。"
						>
							${e.price_history?.length?O`
										<${Er}
											className="table-wrap compact-table"
										>
											<${_r} size="small">
												<${Sr}>
													<${nt}>
														<${X}>时间<//>
														<${X}>价格<//>
														<${X}>来源<//>
														<${X}>关键词<//>
													<//>
												<//>
												<${Rr}>
													${e.price_history.slice(0,20).map((p,c)=>O`
																<${nt}
																	key=${`${p.observed_at}-${c}`}
																>
																	<${X}
																		>${Ue(p.observed_at)}<//
																	>
																	<${X}
																		>${qe(p.price)}<//
																	>
																	<${X}
																		>${p.source||"-"}<//
																	>
																	<${X}
																		>${p.keyword||"-"}<//
																	>
																<//>
															`)}
												<//>
											<//>
										<//>
									`:O`<${At}
										title="暂无价格历史"
										description="抓到同一商品的价格变化后会显示在这里。"
									/>`}
						<//>

						<${ze}
							title="通知记录"
							description="默认展示最近 15 条通知。"
						>
							${e.notifications?.length?O`
										<${Er}
											className="table-wrap compact-table"
										>
											<${_r} size="small">
												<${Sr}>
													<${nt}>
														<${X}>时间<//>
														<${X}>事件<//>
														<${X}
															className="table-primary-cell"
														>
															关键词
														<//>
													<//>
												<//>
												<${Rr}>
													${e.notifications.slice(0,15).map((p,c)=>O`
																<${nt}
																	key=${`${p.sent_at}-${c}`}
																>
																	<${X}
																		>${Ue(p.sent_at)}<//
																	>
																	<${X}
																		>${p.event_type||"-"}<//
																	>
																	<${X}
																		className="table-primary-cell"
																	>
																		<div className="table-primary-copy">
																			<${ie}
																				variant="body2"
																				className="table-primary-title"
																			>
																				${p.keyword||"-"}
																			<//>
																			<${ie}
																				variant="caption"
																				color="text.secondary"
																				className="table-primary-meta"
																			>
																				${p.umo||"-"}
																			<//>
																		</div>
																	<//>
																<//>
															`)}
												<//>
											<//>
										<//>
									`:O`<${At}
										title="暂无通知记录"
										description="发送过通知后会显示在这里。"
									/>`}
						<//>

						<${ze}
							title="抓取记录"
							description="默认展示最近 15 次抓取结果。"
						>
							${e.fetch_runs?.length?O`
										<${Er}
											className="table-wrap compact-table"
										>
											<${_r} size="small">
												<${Sr}>
													<${nt}>
														<${X}>开始时间<//>
														<${X}>状态<//>
														<${X}>商品数<//>
														<${X}>错误<//>
													<//>
												<//>
												<${Rr}>
													${e.fetch_runs.slice(0,15).map(p=>{let c=ly(p.status);return O`
																<${nt}
																	key=${p.id}
																>
																	<${X}
																		>${Ue(p.started_at)}<//
																	>
																	<${X}>
																		<${Fe}
																			size="small"
																			label=${c.label}
																			color=${c.color}
																			variant=${c.variant}
																		/>
																	<//>
																	<${X}
																		>${p.items_count}<//
																	>
																	<${X}
																		>${p.err_msg||"-"}<//
																	>
																<//>
															`})}
												<//>
											<//>
										<//>
									`:O`<${At}
										title="暂无抓取记录"
										description="开始抓取后这里会展示每次执行的结果。"
									/>`}
						<//>
					<//>
				`:O`
					<${Ce}
						sx=${{display:"grid",placeItems:"center",minHeight:240}}
					>
						<${Wr} />
					<//>
				`}
	`}function IO({open:e,detail:t,onClose:r,onFocusSubscription:o,onRunSubscriptionAction:n,onDelete:s,onDeepSearch:i,deepSearchLoading:a}){return O`
		<${Nl}
			anchor="right"
			open=${e}
			onClose=${r}
			PaperProps=${{sx:{width:{xs:"100%",md:760}}}}
		>
			<${Ce} className="detail-drawer">
				<${GT}
					detail=${t}
					onFocusSubscription=${o}
					onRunSubscriptionAction=${n}
					onDelete=${s}
					onDeepSearch=${i}
					deepSearchLoading=${a}
				/>
			<//>
		<//>
	`}var Yn={minWidth:0,"& .MuiOutlinedInput-root":{borderRadius:"10px",fontSize:"0.875rem"},"& .MuiInputBase-input":{py:"7px",px:"10px"},"& .MuiSelect-select":{py:"7px !important",px:"10px !important",pr:"28px !important"}};function cy(){return O`
		<${Ce}
			sx=${{width:"1px",height:28,bgcolor:"divider",flexShrink:0,display:{xs:"none",md:"block"}}}
		/>
	`}function OW({open:e,count:t,onConfirm:r,onCancel:o,loading:n}){return O`
		<${Fn} open=${e} onClose=${o} maxWidth="xs" fullWidth=${!0}>
			<${Wn}>确认删除<//>
			<${Un}>
				<${ie}>
					即将删除 <strong>${t}</strong> 条商品记录（包含对应的价格历史），此操作不可撤销，确定继续？
				<//>
			<//>
			<${Li}>
				<${pe} onClick=${o} disabled=${n}>取消<//>
				<${pe}
					onClick=${r}
					color="error"
					variant="contained"
					disabled=${n}
				>
					${n?"\u5220\u9664\u4E2D\u2026":"\u786E\u8BA4\u5220\u9664"}
				<//>
			<//>
		<//>
	`}function jO({selectedCount:e,totalCount:t,onSelectAll:r,onClearAll:o,onDelete:n}){let s=e>0&&e===t,i=e>0&&e<t;return O`
		<div className="selection-toolbar">
			<${Os}
				indeterminate=${i}
				checked=${s}
				onChange=${s||i?o:r}
				size="small"
			/>
			<${ie} variant="body2" sx=${{mx:1,minWidth:80}}>
				${e>0?`\u5DF2\u9009 ${e} \u6761`:`\u5171 ${t} \u6761`}
			<//>
			${e>0?O`
						<${pe}
							size="small"
							color="error"
							variant="outlined"
							onClick=${n}
							sx=${{ml:1}}
						>
							删除所选 (${e})
						<//>
						<${pe}
							size="small"
							variant="text"
							onClick=${o}
							sx=${{ml:.5}}
						>
							取消选择
						<//>
					`:null}
		</div>
	`}function YT({notify:e}){let[t,r]=(0,Q.useState)({search:"",subId:"",view:"flat",blockedTerms:"",minPrice:"",maxPrice:"",deepSearched:"all",sortBy:"last_seen_at",sortOrder:"desc"}),[o,n]=(0,Q.useState)([]),[s,i]=(0,Q.useState)(0),[a,l]=(0,Q.useState)(!0),[p,c]=(0,Q.useState)(null),[u,f]=(0,Q.useState)(!1),[v,x]=(0,Q.useState)([]),[h,b]=(0,Q.useState)(new Set),[y,m]=(0,Q.useState)(!1),[g,T]=(0,Q.useState)(!1),[w,$]=(0,Q.useState)(!1),C=In("(max-width: 720px)"),_=(0,Q.useDeferredValue)(t.search),S=(0,Q.useCallback)(()=>b(new Set),[]);async function R(){try{let N=await Me("/api/subscriptions/options");(0,Q.startTransition)(()=>{x(N.items||[])})}catch(N){e(N.message,"error")}}async function j(){try{let N=new URLSearchParams({search:_,sort_by:t.sortBy,sort_order:t.sortOrder});t.subId&&N.set("sub_id",t.subId),t.minPrice!==""&&N.set("min_price",t.minPrice),t.maxPrice!==""&&N.set("max_price",t.maxPrice),t.deepSearched!=="all"&&N.set("deep_searched",t.deepSearched);let V=t.view==="by_subscription"?"/api/items/by-subscription":"/api/items",re=await Me(`${V}?${N.toString()}`);(0,Q.startTransition)(()=>{n(re.items||[]),i(re.total||0),S()})}catch(N){e(N.message,"error")}finally{l(!1)}}(0,Q.useEffect)(()=>{R()},[]),(0,Q.useEffect)(()=>{t.view==="by_subscription"&&t.sortBy==="subscription_count"&&r(N=>({...N,sortBy:"last_seen_at"}))},[t.view,t.sortBy]),(0,Q.useEffect)(()=>{l(!0),j()},[_,t.subId,t.view,t.minPrice,t.maxPrice,t.deepSearched,t.sortBy,t.sortOrder]);async function U(N,V=!1){V&&c(null);let re=await Me(`/api/items/${N}`);return(0,Q.startTransition)(()=>c(re.item)),re.item}async function z(N){f(!0);try{await U(N,!0)}catch(V){f(!1),e(V.message,"error")}}async function Z(N,V,re=""){try{await Me(`/api/subscriptions/${N}/${V}`,{method:"POST"}),await R(),await j(),re&&await U(re),e(V==="check"?"\u8BA2\u9605\u5DF2\u6267\u884C\u68C0\u67E5":"\u8BA2\u9605\u72B6\u6001\u5DF2\u66F4\u65B0","success")}catch(de){e(de.message,"error")}}function B(N){f(!1),r(V=>({...V,subId:String(N),view:"by_subscription"}))}async function D(){if(h.size!==0){T(!0);try{let N=t.subId?parseInt(t.subId,10):0;await Me("/api/items",{method:"DELETE",body:{item_ids:Array.from(h),sub_id:N}}),e(`\u5DF2\u5220\u9664 ${h.size} \u6761\u5546\u54C1\u8BB0\u5F55`,"success"),m(!1),S(),await j()}catch(N){e(N.message,"error")}finally{T(!1)}}}async function q(N){try{let V=t.subId?parseInt(t.subId,10):0;await Me("/api/items",{method:"DELETE",body:{item_ids:[N],sub_id:V}}),e("\u5546\u54C1\u8BB0\u5F55\u5DF2\u5220\u9664","success"),u&&f(!1),S(),await j()}catch(V){e(V.message,"error")}}async function E(N){$(!0);try{let V=await Me(`/api/items/${N}/deep-search`,{method:"POST"});c(V.item),await j(),e("\u6DF1\u5EA6\u641C\u7D22\u5B8C\u6210","success")}catch(V){let re=V.payload?.error?.code;e(re==="CAPTCHA"?"\u89E6\u53D1\u4E86\u95F2\u9C7C\u6ED1\u5757\u9A8C\u8BC1\uFF0C\u672C\u6B21\u6DF1\u5EA6\u641C\u7D22\u5DF2\u5931\u8D25\uFF0C\u4E0D\u652F\u6301\u81EA\u52A8\u8FC7\u9A8C\u8BC1\uFF0C\u8BF7\u7A0D\u540E\u91CD\u8BD5":re==="AUTH_REQUIRED"?"\u95F2\u9C7C\u767B\u5F55\u6001\u5DF2\u8FC7\u671F\uFF0C\u8BF7\u5148\u91CD\u65B0\u767B\u5F55\u540E\u518D\u8BD5":V.message,"error")}finally{$(!1)}}function F(N){b(V=>{let re=new Set(V);return re.has(N)?re.delete(N):re.add(N),re})}let ae=CO(t.blockedTerms),ye=o.filter(N=>!$O(N,ae)),me=[];if(t.view==="by_subscription"){let N=new Map;for(let V of ye){if(!N.has(V.sub_id)){let de=Kl(V.enabled,V.paused_reason);N.set(V.sub_id,{sub_id:V.sub_id,keyword:V.keyword,umo:V.umo,enabled:V.enabled,paused_reason:V.paused_reason,statusLabel:de.label,statusColor:de.color,statusVariant:de.variant,last_seen_at:V.last_seen_at,items:[]}),me.push(N.get(V.sub_id))}let re=N.get(V.sub_id);re.items.push(V),re.last_seen_at=Math.max(re.last_seen_at||0,V.last_seen_at||0)}}let te=v.find(N=>String(N.id)===String(t.subId||""))||null,ne=o.length-ye.length,ue=ye.length,he=!!(t.search.trim()||t.subId||t.view!=="flat"||t.blockedTerms.trim()||t.minPrice!==""||t.maxPrice!==""||t.deepSearched!=="all"||t.sortBy!=="last_seen_at"||t.sortOrder!=="desc"),be=ye.map(N=>N.item_id),Te=be.length>0&&be.every(N=>h.has(N)),Pe=be.some(N=>h.has(N))&&!Te;function Ke(){b(N=>{let V=new Set(N);return be.forEach(re=>V.add(re)),V})}return C&&u?O`
			<${Ee} spacing=${Lt.pageGap} className="page-enter page-stack">
				<${tn}
					title="商品详情"
					description="窄屏下切换为单页详情视图，返回后继续保留当前筛选条件。"
					action=${O`
						<${pe} variant="outlined" onClick=${()=>f(!1)}>
							返回列表
						<//>
					`}
				/>
				<${GT}
					detail=${p}
					onFocusSubscription=${B}
					onRunSubscriptionAction=${Z}
					onDelete=${q}
					onDeepSearch=${E}
					deepSearchLoading=${w}
				/>
			<//>
		`:O`
		<${Ee} spacing=${Lt.pageGap} className="page-enter page-stack">
			<${tn}
				title="商品记录"
				description="查看、搜索、过滤已抓取的商品，支持多选批量删除。"
			/>

			${""}
			<${ze}>
				<${Ce} sx=${{display:"flex",flexDirection:"column",gap:1}}>
					${""}
					<${Ce} className="filter-bar-row">
						<${Hr}
							size="small"
							variant="outlined"
							placeholder="搜索标题 / 商品 ID"
							value=${t.search}
							onChange=${N=>r(V=>({...V,search:N.target.value}))}
							sx=${{...Yn,flex:"2 1 200px"}}
						/>
						<${Hr}
							size="small"
							variant="outlined"
							select=${!0}
							value=${t.subId}
							onChange=${N=>r(V=>({...V,subId:N.target.value}))}
							sx=${{...Yn,flex:"1 1 150px"}}
						>
							<${dt} value="">全部订阅<//>
							${v.map(N=>O`
								<${dt} key=${N.id} value=${String(N.id)}>
									${`#${N.id} ${N.keyword}${N.enabled?"":" (\u5DF2\u6682\u505C)"}`}
								<//>
							`)}
						<//>
						<${Hr}
							size="small"
							variant="outlined"
							placeholder="屏蔽词（仅隐藏，不删除）"
							value=${t.blockedTerms}
							onChange=${N=>r(V=>({...V,blockedTerms:N.target.value}))}
							sx=${{...Yn,flex:"1 1 160px"}}
						/>
						${he?O`
									<${pe}
										size="small"
										variant="outlined"
										onClick=${()=>r({search:"",subId:"",view:"flat",blockedTerms:"",minPrice:"",maxPrice:"",deepSearched:"all",sortBy:"last_seen_at",sortOrder:"desc"})}
										sx=${{flexShrink:0,height:36}}
									>
										清除
									<//>
								`:null}
					<//>

					${""}
					<${Ce} className="filter-bar-row">
						<${Hr}
							size="small"
							variant="outlined"
							select=${!0}
							value=${t.view}
							onChange=${N=>r(V=>({...V,view:N.target.value}))}
							sx=${{...Yn,flex:"0 0 110px"}}
						>
							<${dt} value="flat">聚合去重<//>
							<${dt} value="by_subscription">按订阅<//>
						<//>
						<${cy} />
						<${Hr}
							size="small"
							variant="outlined"
							type="number"
							placeholder="最低价"
							value=${t.minPrice}
							onChange=${N=>r(V=>({...V,minPrice:N.target.value}))}
							sx=${{...Yn,flex:"0 1 90px"}}
						/>
						<${ie} variant="body2" color="text.secondary" sx=${{flexShrink:0,lineHeight:"36px"}}>—<//>
						<${Hr}
							size="small"
							variant="outlined"
							type="number"
							placeholder="最高价"
							value=${t.maxPrice}
							onChange=${N=>r(V=>({...V,maxPrice:N.target.value}))}
							sx=${{...Yn,flex:"0 1 90px"}}
						/>
						<${cy} />
						<${Hr}
							size="small"
							variant="outlined"
							select=${!0}
							value=${t.deepSearched}
							onChange=${N=>r(V=>({...V,deepSearched:N.target.value}))}
							sx=${{...Yn,flex:"0 0 130px"}}
						>
							<${dt} value="all">全部（深度搜索）<//>
							<${dt} value="yes">已深度搜索<//>
							<${dt} value="no">未深度搜索<//>
						<//>
						<${cy} />
						<${Hr}
							size="small"
							variant="outlined"
							select=${!0}
							value=${t.sortBy}
							onChange=${N=>r(V=>({...V,sortBy:N.target.value}))}
							sx=${{...Yn,flex:"0 0 110px"}}
						>
							<${dt} value="last_seen_at">最近发现<//>
							<${dt} value="price">价格<//>
							<${dt} value="publish_time">发布时间<//>
							<${dt} value="title">标题<//>
							${t.view==="flat"?O`<${dt} value="subscription_count">订阅数<//>`:null}
						<//>
						<${Hr}
							size="small"
							variant="outlined"
							select=${!0}
							value=${t.sortOrder}
							onChange=${N=>r(V=>({...V,sortOrder:N.target.value}))}
							sx=${{...Yn,flex:"0 0 72px"}}
						>
							<${dt} value="desc">降序<//>
							<${dt} value="asc">升序<//>
						<//>
						<${cy} />
						<${ie}
							variant="caption"
							color="text.secondary"
							sx=${{flexShrink:0,lineHeight:"36px",whiteSpace:"nowrap"}}
						>
							${ue} / ${s} 条
							${ne?O`<span> · 屏蔽 ${ne}</span>`:null}
						<//>
					<//>
				<//>
			<//>

			${""}
			${t.view==="by_subscription"?O`
						<${ze}
							title="按订阅分类"
							description="把商品还原到各条订阅下，便于逐条管理。"
						>
							${a?O`<${Xo} sx=${{mb:2}} />`:null}
							${me.length?O`
										<${Ee} spacing=${Lt.sectionGap}>
											${me.map(N=>O`
													<${ze}
														key=${N.sub_id}
														title=${`#${N.sub_id} \xB7 ${N.keyword}`}
														description=${`${N.items.length} \u6761\u5546\u54C1 \xB7 \u6700\u8FD1\u53D1\u73B0 ${Ue(N.last_seen_at)}`}
														action=${O`
															<div className="header-actions">
																<${Fe}
																	size="small"
																	label=${N.statusLabel}
																	color=${N.statusColor}
																	variant=${N.statusVariant}
																/>
																<${pe}
																	size="small"
																	onClick=${()=>Z(N.sub_id,"check")}
																>
																	立即检查
																<//>
																<${pe}
																	size="small"
																	onClick=${()=>Z(N.sub_id,N.enabled?"pause":"resume")}
																>
																	${N.enabled?"\u6682\u505C":"\u6062\u590D"}
																<//>
																${String(t.subId||"")!==String(N.sub_id)?O`
																			<${pe}
																				size="small"
																				onClick=${()=>B(N.sub_id)}
																			>
																				仅看此订阅
																			<//>
																		`:null}
															</div>
														`}
													>
														<${Er}
															className="table-wrap compact-table managed-table"
														>
															<${_r} size="small">
																<${Sr}>
																	<${nt}>
																		<${X}
																			padding="checkbox"
																			sx=${{width:40}}
																		>
																			<${eu}
																				title="全选本组"
																			>
																				<${Os}
																					size="small"
																					indeterminate=${N.items.some(V=>h.has(V.item_id))&&!N.items.every(V=>h.has(V.item_id))}
																					checked=${N.items.every(V=>h.has(V.item_id))}
																					onChange=${()=>{let V=N.items.every(re=>h.has(re.item_id));b(re=>{let de=new Set(re);return N.items.forEach(ge=>{V?de.delete(ge.item_id):de.add(ge.item_id)}),de})}}
																				/>
																			<//>
																		<//>
																		<${X}
																			className="table-primary-cell"
																		>
																			商品
																		<//>
																		<${X}>价格<//>
																		<${X}>最近发现<//>
																		<${X}>最新事件<//>
																		<${X}>深度搜索<//>
																		<${X}
																			align="right"
																			className="table-action-cell"
																		>
																			操作
																		<//>
																	<//>
																<//>
																<${Rr}>
																	${N.items.map(V=>O`
																			<${nt}
																				key=${`${N.sub_id}-${V.item_id}`}
																				hover=${!0}
																				selected=${h.has(V.item_id)}
																			>
																				<${X}
																					padding="checkbox"
																				>
																					<${Os}
																						size="small"
																						checked=${h.has(V.item_id)}
																						onChange=${()=>F(V.item_id)}
																					/>
																				<//>
																				<${X}
																					className="table-primary-cell"
																				>
																					<div className="table-primary-copy item-primary-copy">
																						<${ie}
																							variant="subtitle2"
																							className="table-primary-title item-primary-title"
																						>
																							${V.title}
																						<//>
																						<${ie}
																							variant="caption"
																							color="text.secondary"
																							className="table-primary-meta"
																						>
																							${V.item_id}
																						<//>
																					</div>
																				<//>
																				<${X}>
																					${qe(V.price)}
																				<//>
																				<${X}>
																					${Ue(V.last_seen_at)}
																				<//>
																				<${X}>
																					${V.latest_event_type||"-"}
																				<//>
																				<${X}>
																					<${Fe}
																						size="small"
																						label=${V.has_deep_analysis?"\u5DF2\u641C\u7D22":"\u672A\u641C\u7D22"}
																						color=${V.has_deep_analysis?"success":"default"}
																						variant=${V.has_deep_analysis?"filled":"outlined"}
																					/>
																				<//>
																				<${X}
																					align="right"
																					className="table-action-cell"
																				>
																					<div className="table-actions">
																						<${pe}
																							size="small"
																							onClick=${()=>z(V.item_id)}
																						>
																							详情
																						<//>
																						<${pe}
																							size="small"
																							variant="outlined"
																							href=${V.url}
																							target="_blank"
																						>
																							打开
																						<//>
																						<${pe}
																							size="small"
																							color="error"
																							onClick=${()=>q(V.item_id)}
																						>
																							删除
																						<//>
																					</div>
																				<//>
																			<//>
																		`)}
																<//>
															<//>
														<//>
													<//>
												`)}
										<//>
									`:O`
										<${At}
											title="没有匹配的订阅商品"
											description="可以切换回「聚合去重」视图，或缩小搜索条件后再试。"
										/>
									`}

							${""}
							${h.size>0?O`
										<${jO}
											selectedCount=${h.size}
											totalCount=${ue}
											onSelectAll=${Ke}
											onClearAll=${S}
											onDelete=${()=>m(!0)}
										/>
									`:null}
						<//>
					`:O`
						${""}
						<${ze}
							title="商品列表"
							description="按商品去重聚合，快速浏览当前库存的所有商品。"
						>
							${a?O`<${Xo} sx=${{mb:2}} />`:null}

							${""}
							<${jO}
								selectedCount=${h.size}
								totalCount=${ue}
								onSelectAll=${Ke}
								onClearAll=${S}
								onDelete=${()=>m(!0)}
							/>

							${ye.length?O`
										<${Er}
											className="table-wrap relaxed-table managed-table"
										>
											<${_r} size="small">
												<${Sr}>
													<${nt}>
														<${X}
															padding="checkbox"
															sx=${{width:40}}
														>
															<${eu} title="全选当前列表">
																<${Os}
																	size="small"
																	indeterminate=${Pe}
																	checked=${Te}
																	onChange=${Te?S:Ke}
																/>
															<//>
														<//>
														<${X} className="table-primary-cell">
															商品
														<//>
														<${X}>价格<//>
														<${X}>最近发现<//>
														<${X}>订阅数<//>
														<${X}>最新事件<//>
														<${X}>深度搜索<//>
														<${X}
															align="right"
															className="table-action-cell"
														>
															操作
														<//>
													<//>
												<//>
												<${Rr}>
													${ye.map(N=>O`
															<${nt}
																key=${N.item_id}
																hover=${!0}
																selected=${h.has(N.item_id)}
															>
																<${X} padding="checkbox">
																	<${Os}
																		size="small"
																		checked=${h.has(N.item_id)}
																		onChange=${()=>F(N.item_id)}
																	/>
																<//>
																<${X}
																	className="table-primary-cell"
																>
																	<div className="table-primary-copy item-primary-copy">
																		<${ie}
																			variant="subtitle2"
																			className="table-primary-title item-primary-title"
																		>
																			${N.title}
																		<//>
																		<${ie}
																			variant="caption"
																			color="text.secondary"
																			className="table-primary-meta"
																		>
																			${N.item_id}
																		<//>
																	</div>
																<//>
																<${X}>
																	${qe(N.price)}
																<//>
																<${X}>
																	${Ue(N.last_seen_at)}
																<//>
																<${X}>
																	${N.subscription_count}
																<//>
																<${X}>
																	${N.latest_event_type||"-"}
																<//>
																<${X}>
																	<${Fe}
																		size="small"
																		label=${N.has_deep_analysis?"\u5DF2\u641C\u7D22":"\u672A\u641C\u7D22"}
																		color=${N.has_deep_analysis?"success":"default"}
																		variant=${N.has_deep_analysis?"filled":"outlined"}
																	/>
																<//>
																<${X}
																	align="right"
																	className="table-action-cell"
																>
																	<div className="table-actions">
																		<${pe}
																			size="small"
																			onClick=${()=>z(N.item_id)}
																		>
																			详情
																		<//>
																		<${pe}
																			size="small"
																			color="error"
																			onClick=${()=>q(N.item_id)}
																		>
																			删除
																		<//>
																	</div>
																<//>
															<//>
														`)}
												<//>
											<//>
										<//>
									`:O`
										<${At}
											title="没有匹配的商品"
											description="输入标题关键词或商品 ID 搜索，或切换到「按订阅分类」视图。"
										/>
									`}
						<//>
					`}

			${""}
			<${OW}
				open=${y}
				count=${h.size}
				loading=${g}
				onConfirm=${D}
				onCancel=${()=>m(!1)}
			/>

			${""}
			${C?null:O`
						<${IO}
							open=${u}
							detail=${p}
							onClose=${()=>f(!1)}
							onFocusSubscription=${B}
							onRunSubscriptionAction=${Z}
							onDelete=${q}
							onDeepSearch=${E}
							deepSearchLoading=${w}
						/>
					`}
		<//>
	`}function XT({notify:e}){let[t,r]=(0,Q.useState)(null),[o,n]=(0,Q.useState)(null),[s,i]=(0,Q.useState)([]),[a,l]=(0,Q.useState)(!0);async function p(u=!1){try{let[f,v,x]=await Promise.all([Me("/api/overview"),Me(`/api/provider/health${u?"?refresh=true":""}`),Me("/api/fetch-runs?limit=20")]);(0,Q.startTransition)(()=>{r(f),n(v.health),i(x.items||[])})}catch(f){e(f.message,"error")}finally{l(!1)}}(0,Q.useEffect)(()=>{p();let u=window.setInterval(()=>p(!1),8e3);return()=>window.clearInterval(u)},[]);let c=[{label:"Provider \u6A21\u5F0F",value:o?.provider||t?.provider_mode||"-"},{label:"Provider \u72B6\u6001",value:o?.ok?"\u53EF\u7528":"\u5F02\u5E38"},{label:"\u8BA4\u8BC1\u72B6\u6001",value:o?.auth||"-"},{label:"\u767B\u5F55\u6001\u6587\u4EF6",value:o?.storage_state===null||o?.storage_state===void 0?"-":o.storage_state?"\u5DF2\u5C31\u7EEA":"\u672A\u627E\u5230"},{label:"\u6700\u8FD1\u5065\u5EB7\u68C0\u67E5",value:Ue(o?.checked_at)},{label:"\u961F\u5217 / \u6267\u884C\u4E2D",value:`${t?.queue_size||0} / ${t?.inflight||0}`}];return O`
		<${Ee} spacing=${Lt.pageGap} className="page-enter page-stack">
			<${tn}
				title="运行状态"
				description="关注 Provider 健康、认证状态与最近抓取执行结果。"
				action=${O`
					<${pe} variant="contained" onClick=${()=>p(!0)}>
						刷新健康检查
					<//>
				`}
			/>

			${a?O`<${Xo} />`:null}

			<div className="stats-grid">
				<${vn}
					label="调度器"
					value=${t?.scheduler_running?"\u8FD0\u884C\u4E2D":"\u672A\u8FD0\u884C"}
					hint=${`\u961F\u5217 ${t?.queue_size||0}\uFF0C\u6267\u884C\u4E2D ${t?.inflight||0}`}
					tone="primary"
				/>
				<${vn}
					label="Provider"
					value=${t?.provider_mode||"-"}
					hint=${t?.provider_error||"\u5F53\u524D\u72B6\u6001\u6B63\u5E38"}
					tone="secondary"
				/>
				<${vn}
					label="认证状态"
					value=${o?.auth||"-"}
					hint=${o?.storage_state?"\u767B\u5F55\u6001\u6587\u4EF6\u5DF2\u5C31\u7EEA":"\u767B\u5F55\u6001\u6587\u4EF6\u5F85\u786E\u8BA4"}
					tone="success"
				/>
				<${vn}
					label="最近健康检查"
					value=${Ue(o?.checked_at)}
					hint="默认每 8 秒自动刷新"
					tone="warning"
				/>
			</div>

			<div className="content-grid runtime-grid">
				<${ze}
					className="runtime-summary-card"
					title="状态摘要"
					description="快速确认当前是否可以正常抓取。"
				>
					${o?.provider_error||t?.provider_error?O`<${Ur}
								severity="error"
								variant="outlined"
								sx=${{mb:2}}
							>
								${o?.provider_error||t?.provider_error}
							<//>`:null}
					<${ra} items=${c} />
				<//>

				<${ze}
					className="runtime-runs-card"
					title="最近抓取记录"
					description="展示最近 20 次抓取执行状态。"
				>
					${s.length?O`
								<${Er}
									className="table-wrap compact-table runtime-runs-table"
								>
									<${_r} size="small">
										<${Sr}>
											<${nt}>
												<${X}>关键词<//>
												<${X}>状态<//>
												<${X}>开始 / 结束<//>
												<${X}>商品数<//>
												<${X}>错误<//>
											<//>
										<//>
										<${Rr}>
											${s.map(u=>{let f=ly(u.status);return O`
													<${nt} key=${u.id}>
														<${X}
															className="table-primary-cell runtime-runs-keyword-cell"
														>
															<div className="table-primary-copy">
																<${ie}
																	variant="body2"
																	className="table-primary-title"
																>
																	${u.keyword}
																<//>
																<${ie}
																	variant="caption"
																	color="text.secondary"
																	className="table-primary-meta"
																>
																	${u.umo}
																<//>
															</div>
														<//>
														<${X}>
															<${Fe}
																size="small"
																label=${f.label}
																color=${f.color}
																variant=${f.variant}
															/>
														<//>
														<${X}>
															<div className="runtime-runs-time">
															<${ie}
																variant="body2"
																>${Ue(u.started_at)}<//
															>
															<${ie}
																variant="caption"
																color="text.secondary"
															>
																${Ue(u.finished_at)}
															<//>
															</div>
														<//>
														<${X}
															>${u.items_count}<//
														>
														<${X}
															>${u.err_msg||u.err_type||"-"}<//
														>
													<//>
												`})}
										<//>
									<//>
								<//>
							`:O`<${At}
								title="暂无抓取记录"
								description="开始执行订阅后，这里会出现抓取结果。"
							/>`}
				<//>
			</div>
		<//>
	`}function QT({notify:e}){let[t,r]=(0,Q.useState)(null),[o,n]=(0,Q.useState)({}),[s,i]=(0,Q.useState)({}),[a,l]=(0,Q.useState)(""),[p,c]=(0,Q.useState)(null);async function u(){try{let h=await Me("/api/config");(0,Q.startTransition)(()=>{r(h.config),n(h.config.values||{}),i({})})}catch(h){e(h.message,"error")}}(0,Q.useEffect)(()=>{u()},[]);async function f(){try{let h=await Me("/api/config",{method:"PUT",body:{values:o}}),b=Object.keys(h.diff||{}).length;l(b?`\u5DF2\u4FDD\u5B58 ${b} \u9879\u914D\u7F6E\u53D8\u66F4\u3002`:"\u6CA1\u6709\u68C0\u6D4B\u5230\u914D\u7F6E\u53D8\u5316\u3002"),i({}),e("\u914D\u7F6E\u5DF2\u4FDD\u5B58","success")}catch(h){i(h.payload?.field_errors||{}),e(h.message,"error")}}async function v(){try{let h=await Me("/api/config/reload",{method:"POST"});c(h),e("\u8FD0\u884C\u65F6\u914D\u7F6E\u5DF2\u91CD\u8F7D","success"),u()}catch(h){e(h.message,"error")}}function x(h){let b=t.schema[h]||{},y=b.type==="list"||b.type==="file"||h.includes("prompt")||h==="remote_headers",m=y,g=h.endsWith("api_key")||h==="remote_api_key",T=Array.isArray(b.options)&&b.options.length>0,w=b.type==="list"||b.type==="file"?Array.isArray(o[h])?o[h].join(`
`):"":o[h]??"";return b.type==="bool"?O`
				<div key=${h} className="field-shell field-shell-wide">
					<div className="switch-row">
						<div>
							<div className="switch-title">
								${b.description||h}
							</div>
							<div className="switch-hint">
								${s[h]||b.hint||""}
							</div>
						</div>
						<${yn}
							checked=${!!o[h]}
							onChange=${$=>n(C=>({...C,[h]:$.target.checked}))}
						/>
					</div>
				</div>
			`:O`
			<${Ce}
				key=${h}
				sx=${{gridColumn:m?"1 / -1":"auto"}}
			>
				<${mr}
					select=${T}
					label=${b.description||h}
					type=${g?"password":b.type==="int"||b.type==="float"?"number":"text"}
					value=${w}
					onChange=${$=>n(C=>({...C,[h]:b.type==="list"||b.type==="file"?$.target.value.split(`
`).map(_=>_.trim()).filter(Boolean):$.target.value}))}
					hint=${b.hint||""}
					error=${s[h]||""}
					multiline=${y}
					minRows=${y?4:1}
				>
					${T?b.options.map($=>O`
									<${dt} key=${$} value=${$}
										>${$}<//
									>
								`):null}
				<//>
			<//>
		`}return t?O`
		<${Ee} spacing=${Lt.pageGap} className="page-enter page-stack">
			<${tn}
				title="运行时配置"
				description="直接编辑覆盖层配置并在运行时重载。"
				meta=${`\u8986\u76D6\u5C42\u6587\u4EF6\uFF1A${t.overlay_path}`}
				action=${O`
					<div className="chip-row">
						<${pe} variant="outlined" onClick=${u}>刷新<//>
						<${pe} variant="contained" onClick=${f}>保存<//>
						<${pe}
							variant="contained"
							color="secondary"
							onClick=${v}
							>应用重载<//
						>
					</div>
				`}
			/>

			${a?O`<${Ur} severity="success" variant="outlined"
						>${a}<//
					>`:null}
			${p?O`
						<${Ur}
							severity=${p.provider_error?"warning":"success"}
							variant="outlined"
						>
							${p.admin_server_restart_required?"\u7BA1\u7406\u540E\u53F0\u76D1\u542C\u5730\u5740\u76F8\u5173\u914D\u7F6E\u5DF2\u4FEE\u6539\uFF0C\u9700\u8981\u91CD\u542F\u63D2\u4EF6\u540E\u751F\u6548\u3002":"\u8FD0\u884C\u65F6\u914D\u7F6E\u5DF2\u751F\u6548\u3002"}
							${p.provider_error?` \u5F53\u524D Provider \u72B6\u6001\u5F02\u5E38\uFF1A${p.provider_error}`:""}
						<//>
					`:null}

			<div className="config-groups">
				${t.groups.map(h=>O`
						<${ze} key=${h.id} title=${h.title}>
							<div className="form-grid">
								${h.fields.map(b=>x(b))}
							</div>
						<//>
					`)}
			</div>
		<//>
	`:O`
			<${Ce} sx=${{display:"grid",placeItems:"center",py:12}}>
				<${Wr} />
			<//>
		`}function DO(e){let t=e==="dark";return Ss({palette:{mode:e,primary:{main:t?"#d4b06f":"#9f8550"},secondary:{main:t?"#b79b65":"#7d6942"},success:{main:"#22c55e"},warning:{main:"#f59e0b"},error:{main:"#ef4444"},background:{default:t?"#16120d":"#f6f1e7",paper:t?"#211b14":"#fdfaf4"},text:{primary:t?"#f4ead8":"#30261a",secondary:t?"#b8ab95":"#7b6d5a"}},shape:{borderRadius:18},typography:{fontFamily:"'Avenir Next', 'Segoe UI Variable', 'PingFang SC', 'Noto Sans SC', sans-serif",h4:{fontWeight:720,letterSpacing:"-0.03em"},h5:{fontWeight:700,letterSpacing:"-0.02em"},h6:{fontWeight:700},subtitle1:{fontWeight:650},subtitle2:{fontWeight:650},button:{textTransform:"none",fontWeight:650}},components:{MuiCssBaseline:{styleOverrides:{body:{minHeight:"100vh"}}},MuiAppBar:{styleOverrides:{root:{borderRadius:24,background:t?"rgba(31, 26, 20, 0.78)":"rgba(253, 250, 244, 0.82)",color:t?"#f4ead8":"#30261a",border:`1px solid ${t?"rgba(212, 176, 111, 0.16)":"rgba(167, 145, 102, 0.16)"}`,boxShadow:t?"0 18px 40px rgba(0, 0, 0, 0.3)":"0 18px 40px rgba(112, 93, 60, 0.09)",backdropFilter:"blur(22px) saturate(180%)",WebkitBackdropFilter:"blur(22px) saturate(180%)"}}},MuiCard:{styleOverrides:{root:{borderRadius:24,background:t?"rgba(33, 27, 20, 0.96)":"rgba(253, 250, 244, 0.96)",border:`1px solid ${t?"rgba(212, 176, 111, 0.12)":"rgba(167, 145, 102, 0.14)"}`,boxShadow:t?"0 18px 40px rgba(0, 0, 0, 0.3)":"0 16px 40px rgba(112, 93, 60, 0.07)"}}},MuiButton:{styleOverrides:{root:{minHeight:40,borderRadius:14,paddingInline:16},contained:{backgroundColor:t?"#c9a463":"#9f8550",boxShadow:"none","&:hover":{backgroundColor:t?"#b89253":"#8f7648",boxShadow:"none"}},outlined:{borderColor:t?"rgba(212, 176, 111, 0.28)":"rgba(167, 145, 102, 0.28)",backgroundColor:t?"rgba(43, 36, 28, 0.9)":"rgba(250, 246, 237, 0.9)"},text:{color:t?"#d2bc94":"#6f5d3e"}}},MuiChip:{styleOverrides:{root:{borderRadius:999,fontWeight:650}}},MuiTableCell:{styleOverrides:{head:{color:t?"#c9b593":"#8a7a63",fontWeight:700,backgroundColor:t?"rgba(39, 33, 25, 0.92)":"rgba(249, 244, 233, 0.92)"},root:{borderBottom:`1px solid ${t?"rgba(91, 76, 56, 0.92)":"rgba(231, 222, 203, 0.92)"}`,verticalAlign:"top"}}},MuiDialog:{styleOverrides:{paper:{borderRadius:24,border:`1px solid ${t?"rgba(212, 176, 111, 0.16)":"rgba(167, 145, 102, 0.16)"}`,boxShadow:t?"0 24px 64px rgba(0, 0, 0, 0.42)":"0 24px 64px rgba(112, 93, 60, 0.12)"}}},MuiDrawer:{styleOverrides:{paper:{background:t?"rgba(24, 20, 15, 0.98)":"rgba(252, 249, 242, 0.98)",borderLeft:`1px solid ${t?"rgba(212, 176, 111, 0.14)":"rgba(167, 145, 102, 0.14)"}`}}}}})}var LO=DO("light"),AO=DO("dark");var BO="(max-width: 1119px)",NW=8e3,MW=2e3,zO={keyword:"",pages:1,price_min:"",price_max:"",personal_only:!1,free_shipping:!1,new_publish_option:"",region:"",preview:null,loading:!1},IW=typeof window<"u"&&window.matchMedia(BO).matches;function jW(){let[e,t]=(0,Q.useState)(WT()),[r,o]=(0,Q.useState)(!1),[n,s]=(0,Q.useState)(!0),[i,a]=(0,Q.useState)(!1),[l,p]=(0,Q.useState)(""),[c,u]=(0,Q.useState)(!1),[f,v]=(0,Q.useState)({open:!1,message:"",severity:"success"}),[x,h]=(0,Q.useState)(IW),[b,y]=(0,Q.useState)(zO),[m,g]=(0,Q.useState)({summary:null,items:[]}),T=In("(prefers-color-scheme: dark)"),[w,$]=(0,Q.useState)(()=>Us?document.documentElement.dataset.theme==="dark":null),C=w??T,_=C?AO:LO,S=In(BO);(0,Q.useEffect)(()=>{if(Us)return Us.onContext(te=>{typeof te?.isDark=="boolean"&&$(te.isDark)})},[]),(0,Q.useEffect)(()=>{document.documentElement.dataset.theme=C?"dark":"light"},[C]);function R(te,ne="success"){v({open:!0,message:te,severity:ne})}function j(te){y(ne=>({...ne,...te}))}async function U(){let te=String(b.keyword||"").trim();if(!(!te||b.loading)){j({loading:!0});try{let ne=await Me("/api/query",{method:"POST",body:{keyword:te,pages:Number(b.pages||1),price_min:b.price_min===""||b.price_min==null?null:Number(b.price_min),price_max:b.price_max===""||b.price_max==null?null:Number(b.price_max),personal_only:!!b.personal_only,free_shipping:!!b.free_shipping,new_publish_option:String(b.new_publish_option||"").trim(),region:String(b.region||"").trim()}});y(ue=>({...ue,keyword:te,pages:Number(ue.pages||1),preview:ne.preview,loading:!1})),R("\u4E34\u65F6\u67E5\u8BE2\u5DF2\u5B8C\u6210","success")}catch(ne){j({loading:!1}),R(ne.message,"error")}}}async function z(){try{await Me("/api/overview"),o(!0)}catch(te){te.code!=="UNAUTHORIZED"&&R(te.message,"error"),o(!1)}finally{s(!1)}}(0,Q.useEffect)(()=>{z();let te=()=>t(WT());return window.addEventListener("hashchange",te),()=>window.removeEventListener("hashchange",te)},[]),(0,Q.useEffect)(()=>{if(!r){g({summary:null,items:[]}),y(zO);return}let te=!1,ne=null;async function ue(){let he=NW;try{let be=await Me("/api/activity-monitor");(Number(be?.summary?.active_count||0)>0||Number(be?.summary?.queue_size||0)>0||Number(be?.summary?.inflight||0)>0)&&(he=MW),te||g(be)}catch(be){if(be.code==="UNAUTHORIZED"){o(!1);return}}finally{te||(ne=window.setTimeout(ue,he))}}return ue(),()=>{te=!0,ne&&window.clearTimeout(ne)}},[r]);async function Z(te){a(!0),p("");try{await Me("/api/admin/login",{method:"POST",body:{api_key:te}}),o(!0),R("\u767B\u5F55\u6210\u529F","success"),z()}catch(ne){p(ne.message)}finally{a(!1)}}async function B(){try{await Me("/api/admin/logout",{method:"POST"})}catch{}o(!1)}let D=m.summary||{},q=m.items||[],E=Number(D.active_count||0)>0||Number(D.queue_size||0)>0||Number(D.inflight||0)>0,F=q[0]||null,ae=F?`${F.phase_label} \xB7 ${F.keyword}`:`\u6392\u961F ${D.queue_size||0} \xB7 \u6D3B\u8DC3 ${D.active_count||0}`;if((0,Q.useEffect)(()=>{E||h(!1)},[E]),n)return O`
			<${nl} theme=${_}>
				<${Cl} />
				<${Ce}
					sx=${{minHeight:"100vh",display:"grid",placeItems:"center"}}
				>
					<${Wr} />
				<//>
			<//>
		`;if(!r)return O`
			<${nl} theme=${_}>
				<${Cl} />
				<${kO}
					loading=${i}
					error=${l}
					onLogin=${Z}
				/>
			<//>
		`;let ye=Hl.find(te=>te.key===e)||Hl[0],me=O`
		<${Ee} spacing=${3.5}>
			<div className="brand-row">
				<div className="brand-mark">
					<img
						src="./logo.png"
						alt="Goofish Catcher logo"
						className="brand-mark-img"
					/>
				</div>
				<div>
					<${ie} variant="subtitle1">Goofish Catcher<//>
					<${ie} variant="body2" color="text.secondary"
						>管理后台<//
					>
				</div>
			</div>

			<div className="nav-list">
				${Hl.map(te=>O`
						<button
							type="button"
							key=${te.key}
							onClick=${()=>{VT(te.key),t(te.key),u(!1)}}
							className=${hn("sidebar-nav-button",e===te.key&&"is-active")}
						>
							<div className="sidebar-nav-title">
								${te.label}
							</div>
							<div className="sidebar-nav-desc">
								${te.description}
							</div>
						</button>
					`)}
			</div>
		<//>
	`;return O`
		<${nl} theme=${_}>
			<${Cl} />
			<div className="app-shell">
				${S?O`
							<${Nl}
								open=${c}
								onClose=${()=>u(!1)}
								hideBackdrop=${!0}
								ModalProps=${{keepMounted:!0,disableAutoFocus:!0,disableEnforceFocus:!0,disableRestoreFocus:!0,disableScrollLock:!0}}
								sx=${{pointerEvents:"none"}}
								PaperProps=${{sx:{width:{xs:"calc(100vw - 32px)",sm:320},maxWidth:"100vw",top:{xs:16,sm:20},left:{xs:16,sm:20},right:"auto",bottom:"auto",height:"auto",maxHeight:"calc(100vh - 32px)",background:"transparent",border:"none",boxShadow:"none",overflow:"visible",pointerEvents:"none",p:0}}}
							>
								<div className="app-sidebar mobile-sidebar">
									${me}
								</div>
							<//>
						`:O`
							<div className="app-sidebar desktop-sidebar">
								${me}
							</div>
						`}

				<div className="app-main">
					<div className="app-main-inner">
						<${vm}
							position="sticky"
							elevation=${0}
							className="topbar"
							sx=${{top:{xs:16,sm:20,lg:32}}}
						>
							<${Xm}
								sx=${{minHeight:{xs:64,md:78},px:{xs:1.75,md:3}}}
							>
								${S?O`
											<${pe}
												variant="outlined"
												size="small"
												onClick=${()=>u(te=>!te)}
												sx=${{mr:1.5}}
											>
												${c?"\u6536\u8D77\u5BFC\u822A":"\u5BFC\u822A"}
											<//>
										`:null}
								<${Ce} sx=${{flex:1,minWidth:0}}>
									<${ie} variant="h6"
										>${ye.label}<//
									>
								<//>
								<div className="topbar-actions">
									<div className="topbar-description">
										${ye.description}
									</div>
									${Us?null:O`<${pe} onClick=${B}>退出登录<//>`}
								</div>
							<//>
						<//>

						<div
							className=${hn("page-content",E&&"has-live-monitor",E&&x&&"has-live-monitor-collapsed")}
						>
							${e==="dashboard"?O`<${HT}
										notify=${R}
										temporaryQuery=${b}
										onTemporaryQueryChange=${j}
										onRunTemporaryQuery=${U}
									/>`:null}
							${e==="subscriptions"?O`<${KT}
										notify=${R}
									/>`:null}
							${e==="items"?O`<${YT} notify=${R} />`:null}
							${e==="runtime"?O`<${XT} notify=${R} />`:null}
							${e==="config"?O`<${QT} notify=${R} />`:null}
						</div>
					</div>
				</div>
			</div>

			${E?O`
						<div
							className=${hn("floating-monitor",x&&"is-collapsed")}
						>
							<div className="floating-monitor-shell">
								<div className="floating-monitor-head">
									<div className="floating-monitor-copy">
										<div className="floating-monitor-title">
											<span className="monitor-pulse"></span>
											检查进行中
										</div>
										<div className="floating-monitor-subtitle">
											${x?ae:D.scheduler_running?"\u6293\u53D6\u4E0E\u5206\u6790\u9636\u6BB5\u4F1A\u5728\u8FD9\u91CC\u5B9E\u65F6\u66F4\u65B0":"\u5B58\u5728\u6392\u961F\u6216\u6267\u884C\u4E2D\u7684\u68C0\u67E5\u4EFB\u52A1"}
										</div>
									</div>
									<div className="floating-monitor-actions">
										<${pe}
											className="floating-monitor-action floating-monitor-action-detail"
											size="small"
											variant="text"
											onClick=${()=>{VT("runtime"),t("runtime")}}
										>
											查看详情
										<//>
										<${pe}
											className="floating-monitor-action floating-monitor-action-toggle"
											size="small"
											variant="text"
											onClick=${()=>h(te=>!te)}
										>
											${x?"\u5C55\u5F00\u76D1\u63A7":"\u6536\u8D77\u76D1\u63A7"}
										<//>
									</div>
								</div>

								<div className="floating-monitor-body">
									<div className="floating-monitor-stats">
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												活跃任务
											</span>
											<strong>
												${D.active_count||0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												抓取中
											</span>
											<strong>
												${D.fetching_count||0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												预筛中
											</span>
											<strong>
												${D.prefiltering_count||0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												分析中
											</span>
											<strong>
												${D.analyzing_count||0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												队列
											</span>
											<strong>
												${D.queue_size||0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												Workers
											</span>
											<strong>
												${D.workers||0}
											</strong>
										</div>
									</div>

									${q.length?O`
												<div className="floating-monitor-list">
													${q.map(te=>{let ne=Math.max(1,(D.updated_at||0)-te.started_at);return O`
															<div
																className="floating-monitor-item"
																key=${te.task_id}
															>
																<div className="floating-monitor-item-head">
																	<div className="floating-monitor-item-main">
																		<div className="floating-monitor-item-title">
																			${te.keyword}
																		</div>
																		<div className="floating-monitor-item-meta">
																			${te.source_label} ·
																			${te.phase_label} ·
																			${te.provider_mode}
																		</div>
																	</div>
																	<div className="floating-monitor-phase">
																		${te.progress_pct}%
																	</div>
																</div>
																<${Xo}
																	variant="determinate"
																	value=${te.progress_pct}
																	sx=${{mt:1.25,height:8,borderRadius:999}}
																/>
																${te.message?O`
																			<div className="floating-monitor-item-note">
																				${te.message}
																			</div>
																		`:null}
																<div className="floating-monitor-item-foot">
																	<span>
																		${te.umo||"\u672A\u7ED1\u5B9A UMO"}
																	</span>
																	<span>
																		开始于
																		${Ue(te.started_at)}
																	</span>
																	<span>
																		已运行
																		${ql(ne)}
																	</span>
																</div>
															</div>
														`})}
												</div>
											`:O`
												<div className="floating-monitor-empty">
													任务已入队，等待开始抓取...
												</div>
											`}
								</div>
							</div>
						</div>
					`:null}

			<${Am}
				open=${f.open}
				autoHideDuration=${3200}
				onClose=${()=>v(te=>({...te,open:!1}))}
			>
				<${Ur}
					severity=${f.severity}
					variant="filled"
					onClose=${()=>v(te=>({...te,open:!1}))}
				>
					${f.message}
				<//>
			<//>
		<//>
	`}(0,UT.createRoot)(document.getElementById("root")).render(O`<${jW} />`);})();
/*! Bundled license information:

react/cjs/react.production.min.js:
  (**
   * @license React
   * react.production.min.js
   *
   * Copyright (c) Facebook, Inc. and its affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

scheduler/cjs/scheduler.production.min.js:
  (**
   * @license React
   * scheduler.production.min.js
   *
   * Copyright (c) Facebook, Inc. and its affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

react-dom/cjs/react-dom.production.min.js:
  (**
   * @license React
   * react-dom.production.min.js
   *
   * Copyright (c) Facebook, Inc. and its affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

react-is/cjs/react-is.production.min.js:
  (** @license React v16.13.1
   * react-is.production.min.js
   *
   * Copyright (c) Facebook, Inc. and its affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

react/cjs/react-jsx-runtime.production.min.js:
  (**
   * @license React
   * react-jsx-runtime.production.min.js
   *
   * Copyright (c) Facebook, Inc. and its affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

@mui/styled-engine/node/index.js:
  (**
   * @mui/styled-engine v5.18.0
   *
   * @license MIT
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

react-is/cjs/react-is.production.js:
  (**
   * @license React
   * react-is.production.js
   *
   * Copyright (c) Meta Platforms, Inc. and affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)

@mui/private-theming/index.js:
  (**
   * @mui/private-theming v5.17.1
   *
   * @license MIT
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)
*/
