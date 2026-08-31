var Iv=Object.defineProperty;var Dv=(s,e,t)=>e in s?Iv(s,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):s[e]=t;var lo=(s,e,t)=>Dv(s,typeof e!="symbol"?e+"":e,t);(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const o of document.querySelectorAll('link[rel="modulepreload"]'))r(o);new MutationObserver(o=>{for(const l of o)if(l.type==="childList")for(const d of l.addedNodes)d.tagName==="LINK"&&d.rel==="modulepreload"&&r(d)}).observe(document,{childList:!0,subtree:!0});function t(o){const l={};return o.integrity&&(l.integrity=o.integrity),o.referrerPolicy&&(l.referrerPolicy=o.referrerPolicy),o.crossOrigin==="use-credentials"?l.credentials="include":o.crossOrigin==="anonymous"?l.credentials="omit":l.credentials="same-origin",l}function r(o){if(o.ep)return;o.ep=!0;const l=t(o);fetch(o.href,l)}})();function Qg(s){return s&&s.__esModule&&Object.prototype.hasOwnProperty.call(s,"default")?s.default:s}var hd={exports:{}},co={},pd={exports:{}},xt={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var km;function Uv(){if(km)return xt;km=1;var s=Symbol.for("react.element"),e=Symbol.for("react.portal"),t=Symbol.for("react.fragment"),r=Symbol.for("react.strict_mode"),o=Symbol.for("react.profiler"),l=Symbol.for("react.provider"),d=Symbol.for("react.context"),f=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),m=Symbol.for("react.memo"),_=Symbol.for("react.lazy"),S=Symbol.iterator;function x(k){return k===null||typeof k!="object"?null:(k=S&&k[S]||k["@@iterator"],typeof k=="function"?k:null)}var M={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},w=Object.assign,A={};function v(k,Q,Ue){this.props=k,this.context=Q,this.refs=A,this.updater=Ue||M}v.prototype.isReactComponent={},v.prototype.setState=function(k,Q){if(typeof k!="object"&&typeof k!="function"&&k!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,k,Q,"setState")},v.prototype.forceUpdate=function(k){this.updater.enqueueForceUpdate(this,k,"forceUpdate")};function y(){}y.prototype=v.prototype;function P(k,Q,Ue){this.props=k,this.context=Q,this.refs=A,this.updater=Ue||M}var U=P.prototype=new y;U.constructor=P,w(U,v.prototype),U.isPureReactComponent=!0;var N=Array.isArray,L=Object.prototype.hasOwnProperty,R={current:null},D={key:!0,ref:!0,__self:!0,__source:!0};function E(k,Q,Ue){var $e,Ve={},re=null,_e=null;if(Q!=null)for($e in Q.ref!==void 0&&(_e=Q.ref),Q.key!==void 0&&(re=""+Q.key),Q)L.call(Q,$e)&&!D.hasOwnProperty($e)&&(Ve[$e]=Q[$e]);var me=arguments.length-2;if(me===1)Ve.children=Ue;else if(1<me){for(var Fe=Array(me),Je=0;Je<me;Je++)Fe[Je]=arguments[Je+2];Ve.children=Fe}if(k&&k.defaultProps)for($e in me=k.defaultProps,me)Ve[$e]===void 0&&(Ve[$e]=me[$e]);return{$$typeof:s,type:k,key:re,ref:_e,props:Ve,_owner:R.current}}function I(k,Q){return{$$typeof:s,type:k.type,key:Q,ref:k.ref,props:k.props,_owner:k._owner}}function z(k){return typeof k=="object"&&k!==null&&k.$$typeof===s}function B(k){var Q={"=":"=0",":":"=2"};return"$"+k.replace(/[=:]/g,function(Ue){return Q[Ue]})}var H=/\/+/g;function ce(k,Q){return typeof k=="object"&&k!==null&&k.key!=null?B(""+k.key):Q.toString(36)}function he(k,Q,Ue,$e,Ve){var re=typeof k;(re==="undefined"||re==="boolean")&&(k=null);var _e=!1;if(k===null)_e=!0;else switch(re){case"string":case"number":_e=!0;break;case"object":switch(k.$$typeof){case s:case e:_e=!0}}if(_e)return _e=k,Ve=Ve(_e),k=$e===""?"."+ce(_e,0):$e,N(Ve)?(Ue="",k!=null&&(Ue=k.replace(H,"$&/")+"/"),he(Ve,Q,Ue,"",function(Je){return Je})):Ve!=null&&(z(Ve)&&(Ve=I(Ve,Ue+(!Ve.key||_e&&_e.key===Ve.key?"":(""+Ve.key).replace(H,"$&/")+"/")+k)),Q.push(Ve)),1;if(_e=0,$e=$e===""?".":$e+":",N(k))for(var me=0;me<k.length;me++){re=k[me];var Fe=$e+ce(re,me);_e+=he(re,Q,Ue,Fe,Ve)}else if(Fe=x(k),typeof Fe=="function")for(k=Fe.call(k),me=0;!(re=k.next()).done;)re=re.value,Fe=$e+ce(re,me++),_e+=he(re,Q,Ue,Fe,Ve);else if(re==="object")throw Q=String(k),Error("Objects are not valid as a React child (found: "+(Q==="[object Object]"?"object with keys {"+Object.keys(k).join(", ")+"}":Q)+"). If you meant to render a collection of children, use an array instead.");return _e}function Z(k,Q,Ue){if(k==null)return k;var $e=[],Ve=0;return he(k,$e,"","",function(re){return Q.call(Ue,re,Ve++)}),$e}function ue(k){if(k._status===-1){var Q=k._result;Q=Q(),Q.then(function(Ue){(k._status===0||k._status===-1)&&(k._status=1,k._result=Ue)},function(Ue){(k._status===0||k._status===-1)&&(k._status=2,k._result=Ue)}),k._status===-1&&(k._status=0,k._result=Q)}if(k._status===1)return k._result.default;throw k._result}var K={current:null},q={transition:null},se={ReactCurrentDispatcher:K,ReactCurrentBatchConfig:q,ReactCurrentOwner:R};function le(){throw Error("act(...) is not supported in production builds of React.")}return xt.Children={map:Z,forEach:function(k,Q,Ue){Z(k,function(){Q.apply(this,arguments)},Ue)},count:function(k){var Q=0;return Z(k,function(){Q++}),Q},toArray:function(k){return Z(k,function(Q){return Q})||[]},only:function(k){if(!z(k))throw Error("React.Children.only expected to receive a single React element child.");return k}},xt.Component=v,xt.Fragment=t,xt.Profiler=o,xt.PureComponent=P,xt.StrictMode=r,xt.Suspense=p,xt.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=se,xt.act=le,xt.cloneElement=function(k,Q,Ue){if(k==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+k+".");var $e=w({},k.props),Ve=k.key,re=k.ref,_e=k._owner;if(Q!=null){if(Q.ref!==void 0&&(re=Q.ref,_e=R.current),Q.key!==void 0&&(Ve=""+Q.key),k.type&&k.type.defaultProps)var me=k.type.defaultProps;for(Fe in Q)L.call(Q,Fe)&&!D.hasOwnProperty(Fe)&&($e[Fe]=Q[Fe]===void 0&&me!==void 0?me[Fe]:Q[Fe])}var Fe=arguments.length-2;if(Fe===1)$e.children=Ue;else if(1<Fe){me=Array(Fe);for(var Je=0;Je<Fe;Je++)me[Je]=arguments[Je+2];$e.children=me}return{$$typeof:s,type:k.type,key:Ve,ref:re,props:$e,_owner:_e}},xt.createContext=function(k){return k={$$typeof:d,_currentValue:k,_currentValue2:k,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},k.Provider={$$typeof:l,_context:k},k.Consumer=k},xt.createElement=E,xt.createFactory=function(k){var Q=E.bind(null,k);return Q.type=k,Q},xt.createRef=function(){return{current:null}},xt.forwardRef=function(k){return{$$typeof:f,render:k}},xt.isValidElement=z,xt.lazy=function(k){return{$$typeof:_,_payload:{_status:-1,_result:k},_init:ue}},xt.memo=function(k,Q){return{$$typeof:m,type:k,compare:Q===void 0?null:Q}},xt.startTransition=function(k){var Q=q.transition;q.transition={};try{k()}finally{q.transition=Q}},xt.unstable_act=le,xt.useCallback=function(k,Q){return K.current.useCallback(k,Q)},xt.useContext=function(k){return K.current.useContext(k)},xt.useDebugValue=function(){},xt.useDeferredValue=function(k){return K.current.useDeferredValue(k)},xt.useEffect=function(k,Q){return K.current.useEffect(k,Q)},xt.useId=function(){return K.current.useId()},xt.useImperativeHandle=function(k,Q,Ue){return K.current.useImperativeHandle(k,Q,Ue)},xt.useInsertionEffect=function(k,Q){return K.current.useInsertionEffect(k,Q)},xt.useLayoutEffect=function(k,Q){return K.current.useLayoutEffect(k,Q)},xt.useMemo=function(k,Q){return K.current.useMemo(k,Q)},xt.useReducer=function(k,Q,Ue){return K.current.useReducer(k,Q,Ue)},xt.useRef=function(k){return K.current.useRef(k)},xt.useState=function(k){return K.current.useState(k)},xt.useSyncExternalStore=function(k,Q,Ue){return K.current.useSyncExternalStore(k,Q,Ue)},xt.useTransition=function(){return K.current.useTransition()},xt.version="18.3.1",xt}var Om;function Kf(){return Om||(Om=1,pd.exports=Uv()),pd.exports}/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var zm;function Fv(){if(zm)return co;zm=1;var s=Kf(),e=Symbol.for("react.element"),t=Symbol.for("react.fragment"),r=Object.prototype.hasOwnProperty,o=s.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,l={key:!0,ref:!0,__self:!0,__source:!0};function d(f,p,m){var _,S={},x=null,M=null;m!==void 0&&(x=""+m),p.key!==void 0&&(x=""+p.key),p.ref!==void 0&&(M=p.ref);for(_ in p)r.call(p,_)&&!l.hasOwnProperty(_)&&(S[_]=p[_]);if(f&&f.defaultProps)for(_ in p=f.defaultProps,p)S[_]===void 0&&(S[_]=p[_]);return{$$typeof:e,type:f,key:x,ref:M,props:S,_owner:o.current}}return co.Fragment=t,co.jsx=d,co.jsxs=d,co}var Bm;function kv(){return Bm||(Bm=1,hd.exports=Fv()),hd.exports}var u=kv(),xe=Kf();const Nc=Qg(xe);var Ul={},md={exports:{}},$n={},gd={exports:{}},xd={};/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Vm;function Ov(){return Vm||(Vm=1,(function(s){function e(q,se){var le=q.length;q.push(se);e:for(;0<le;){var k=le-1>>>1,Q=q[k];if(0<o(Q,se))q[k]=se,q[le]=Q,le=k;else break e}}function t(q){return q.length===0?null:q[0]}function r(q){if(q.length===0)return null;var se=q[0],le=q.pop();if(le!==se){q[0]=le;e:for(var k=0,Q=q.length,Ue=Q>>>1;k<Ue;){var $e=2*(k+1)-1,Ve=q[$e],re=$e+1,_e=q[re];if(0>o(Ve,le))re<Q&&0>o(_e,Ve)?(q[k]=_e,q[re]=le,k=re):(q[k]=Ve,q[$e]=le,k=$e);else if(re<Q&&0>o(_e,le))q[k]=_e,q[re]=le,k=re;else break e}}return se}function o(q,se){var le=q.sortIndex-se.sortIndex;return le!==0?le:q.id-se.id}if(typeof performance=="object"&&typeof performance.now=="function"){var l=performance;s.unstable_now=function(){return l.now()}}else{var d=Date,f=d.now();s.unstable_now=function(){return d.now()-f}}var p=[],m=[],_=1,S=null,x=3,M=!1,w=!1,A=!1,v=typeof setTimeout=="function"?setTimeout:null,y=typeof clearTimeout=="function"?clearTimeout:null,P=typeof setImmediate<"u"?setImmediate:null;typeof navigator<"u"&&navigator.scheduling!==void 0&&navigator.scheduling.isInputPending!==void 0&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function U(q){for(var se=t(m);se!==null;){if(se.callback===null)r(m);else if(se.startTime<=q)r(m),se.sortIndex=se.expirationTime,e(p,se);else break;se=t(m)}}function N(q){if(A=!1,U(q),!w)if(t(p)!==null)w=!0,ue(L);else{var se=t(m);se!==null&&K(N,se.startTime-q)}}function L(q,se){w=!1,A&&(A=!1,y(E),E=-1),M=!0;var le=x;try{for(U(se),S=t(p);S!==null&&(!(S.expirationTime>se)||q&&!B());){var k=S.callback;if(typeof k=="function"){S.callback=null,x=S.priorityLevel;var Q=k(S.expirationTime<=se);se=s.unstable_now(),typeof Q=="function"?S.callback=Q:S===t(p)&&r(p),U(se)}else r(p);S=t(p)}if(S!==null)var Ue=!0;else{var $e=t(m);$e!==null&&K(N,$e.startTime-se),Ue=!1}return Ue}finally{S=null,x=le,M=!1}}var R=!1,D=null,E=-1,I=5,z=-1;function B(){return!(s.unstable_now()-z<I)}function H(){if(D!==null){var q=s.unstable_now();z=q;var se=!0;try{se=D(!0,q)}finally{se?ce():(R=!1,D=null)}}else R=!1}var ce;if(typeof P=="function")ce=function(){P(H)};else if(typeof MessageChannel<"u"){var he=new MessageChannel,Z=he.port2;he.port1.onmessage=H,ce=function(){Z.postMessage(null)}}else ce=function(){v(H,0)};function ue(q){D=q,R||(R=!0,ce())}function K(q,se){E=v(function(){q(s.unstable_now())},se)}s.unstable_IdlePriority=5,s.unstable_ImmediatePriority=1,s.unstable_LowPriority=4,s.unstable_NormalPriority=3,s.unstable_Profiling=null,s.unstable_UserBlockingPriority=2,s.unstable_cancelCallback=function(q){q.callback=null},s.unstable_continueExecution=function(){w||M||(w=!0,ue(L))},s.unstable_forceFrameRate=function(q){0>q||125<q?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):I=0<q?Math.floor(1e3/q):5},s.unstable_getCurrentPriorityLevel=function(){return x},s.unstable_getFirstCallbackNode=function(){return t(p)},s.unstable_next=function(q){switch(x){case 1:case 2:case 3:var se=3;break;default:se=x}var le=x;x=se;try{return q()}finally{x=le}},s.unstable_pauseExecution=function(){},s.unstable_requestPaint=function(){},s.unstable_runWithPriority=function(q,se){switch(q){case 1:case 2:case 3:case 4:case 5:break;default:q=3}var le=x;x=q;try{return se()}finally{x=le}},s.unstable_scheduleCallback=function(q,se,le){var k=s.unstable_now();switch(typeof le=="object"&&le!==null?(le=le.delay,le=typeof le=="number"&&0<le?k+le:k):le=k,q){case 1:var Q=-1;break;case 2:Q=250;break;case 5:Q=1073741823;break;case 4:Q=1e4;break;default:Q=5e3}return Q=le+Q,q={id:_++,callback:se,priorityLevel:q,startTime:le,expirationTime:Q,sortIndex:-1},le>k?(q.sortIndex=le,e(m,q),t(p)===null&&q===t(m)&&(A?(y(E),E=-1):A=!0,K(N,le-k))):(q.sortIndex=Q,e(p,q),w||M||(w=!0,ue(L))),q},s.unstable_shouldYield=B,s.unstable_wrapCallback=function(q){var se=x;return function(){var le=x;x=se;try{return q.apply(this,arguments)}finally{x=le}}}})(xd)),xd}var Hm;function zv(){return Hm||(Hm=1,gd.exports=Ov()),gd.exports}/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var jm;function Bv(){if(jm)return $n;jm=1;var s=Kf(),e=zv();function t(n){for(var i="https://reactjs.org/docs/error-decoder.html?invariant="+n,a=1;a<arguments.length;a++)i+="&args[]="+encodeURIComponent(arguments[a]);return"Minified React error #"+n+"; visit "+i+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var r=new Set,o={};function l(n,i){d(n,i),d(n+"Capture",i)}function d(n,i){for(o[n]=i,n=0;n<i.length;n++)r.add(i[n])}var f=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),p=Object.prototype.hasOwnProperty,m=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,_={},S={};function x(n){return p.call(S,n)?!0:p.call(_,n)?!1:m.test(n)?S[n]=!0:(_[n]=!0,!1)}function M(n,i,a,c){if(a!==null&&a.type===0)return!1;switch(typeof i){case"function":case"symbol":return!0;case"boolean":return c?!1:a!==null?!a.acceptsBooleans:(n=n.toLowerCase().slice(0,5),n!=="data-"&&n!=="aria-");default:return!1}}function w(n,i,a,c){if(i===null||typeof i>"u"||M(n,i,a,c))return!0;if(c)return!1;if(a!==null)switch(a.type){case 3:return!i;case 4:return i===!1;case 5:return isNaN(i);case 6:return isNaN(i)||1>i}return!1}function A(n,i,a,c,h,g,T){this.acceptsBooleans=i===2||i===3||i===4,this.attributeName=c,this.attributeNamespace=h,this.mustUseProperty=a,this.propertyName=n,this.type=i,this.sanitizeURL=g,this.removeEmptyString=T}var v={};"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(n){v[n]=new A(n,0,!1,n,null,!1,!1)}),[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(n){var i=n[0];v[i]=new A(i,1,!1,n[1],null,!1,!1)}),["contentEditable","draggable","spellCheck","value"].forEach(function(n){v[n]=new A(n,2,!1,n.toLowerCase(),null,!1,!1)}),["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(n){v[n]=new A(n,2,!1,n,null,!1,!1)}),"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(n){v[n]=new A(n,3,!1,n.toLowerCase(),null,!1,!1)}),["checked","multiple","muted","selected"].forEach(function(n){v[n]=new A(n,3,!0,n,null,!1,!1)}),["capture","download"].forEach(function(n){v[n]=new A(n,4,!1,n,null,!1,!1)}),["cols","rows","size","span"].forEach(function(n){v[n]=new A(n,6,!1,n,null,!1,!1)}),["rowSpan","start"].forEach(function(n){v[n]=new A(n,5,!1,n.toLowerCase(),null,!1,!1)});var y=/[\-:]([a-z])/g;function P(n){return n[1].toUpperCase()}"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(n){var i=n.replace(y,P);v[i]=new A(i,1,!1,n,null,!1,!1)}),"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(n){var i=n.replace(y,P);v[i]=new A(i,1,!1,n,"http://www.w3.org/1999/xlink",!1,!1)}),["xml:base","xml:lang","xml:space"].forEach(function(n){var i=n.replace(y,P);v[i]=new A(i,1,!1,n,"http://www.w3.org/XML/1998/namespace",!1,!1)}),["tabIndex","crossOrigin"].forEach(function(n){v[n]=new A(n,1,!1,n.toLowerCase(),null,!1,!1)}),v.xlinkHref=new A("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1),["src","href","action","formAction"].forEach(function(n){v[n]=new A(n,1,!1,n.toLowerCase(),null,!0,!0)});function U(n,i,a,c){var h=v.hasOwnProperty(i)?v[i]:null;(h!==null?h.type!==0:c||!(2<i.length)||i[0]!=="o"&&i[0]!=="O"||i[1]!=="n"&&i[1]!=="N")&&(w(i,a,h,c)&&(a=null),c||h===null?x(i)&&(a===null?n.removeAttribute(i):n.setAttribute(i,""+a)):h.mustUseProperty?n[h.propertyName]=a===null?h.type===3?!1:"":a:(i=h.attributeName,c=h.attributeNamespace,a===null?n.removeAttribute(i):(h=h.type,a=h===3||h===4&&a===!0?"":""+a,c?n.setAttributeNS(c,i,a):n.setAttribute(i,a))))}var N=s.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,L=Symbol.for("react.element"),R=Symbol.for("react.portal"),D=Symbol.for("react.fragment"),E=Symbol.for("react.strict_mode"),I=Symbol.for("react.profiler"),z=Symbol.for("react.provider"),B=Symbol.for("react.context"),H=Symbol.for("react.forward_ref"),ce=Symbol.for("react.suspense"),he=Symbol.for("react.suspense_list"),Z=Symbol.for("react.memo"),ue=Symbol.for("react.lazy"),K=Symbol.for("react.offscreen"),q=Symbol.iterator;function se(n){return n===null||typeof n!="object"?null:(n=q&&n[q]||n["@@iterator"],typeof n=="function"?n:null)}var le=Object.assign,k;function Q(n){if(k===void 0)try{throw Error()}catch(a){var i=a.stack.trim().match(/\n( *(at )?)/);k=i&&i[1]||""}return`
`+k+n}var Ue=!1;function $e(n,i){if(!n||Ue)return"";Ue=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(i)if(i=function(){throw Error()},Object.defineProperty(i.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(i,[])}catch(oe){var c=oe}Reflect.construct(n,[],i)}else{try{i.call()}catch(oe){c=oe}n.call(i.prototype)}else{try{throw Error()}catch(oe){c=oe}n()}}catch(oe){if(oe&&c&&typeof oe.stack=="string"){for(var h=oe.stack.split(`
`),g=c.stack.split(`
`),T=h.length-1,O=g.length-1;1<=T&&0<=O&&h[T]!==g[O];)O--;for(;1<=T&&0<=O;T--,O--)if(h[T]!==g[O]){if(T!==1||O!==1)do if(T--,O--,0>O||h[T]!==g[O]){var V=`
`+h[T].replace(" at new "," at ");return n.displayName&&V.includes("<anonymous>")&&(V=V.replace("<anonymous>",n.displayName)),V}while(1<=T&&0<=O);break}}}finally{Ue=!1,Error.prepareStackTrace=a}return(n=n?n.displayName||n.name:"")?Q(n):""}function Ve(n){switch(n.tag){case 5:return Q(n.type);case 16:return Q("Lazy");case 13:return Q("Suspense");case 19:return Q("SuspenseList");case 0:case 2:case 15:return n=$e(n.type,!1),n;case 11:return n=$e(n.type.render,!1),n;case 1:return n=$e(n.type,!0),n;default:return""}}function re(n){if(n==null)return null;if(typeof n=="function")return n.displayName||n.name||null;if(typeof n=="string")return n;switch(n){case D:return"Fragment";case R:return"Portal";case I:return"Profiler";case E:return"StrictMode";case ce:return"Suspense";case he:return"SuspenseList"}if(typeof n=="object")switch(n.$$typeof){case B:return(n.displayName||"Context")+".Consumer";case z:return(n._context.displayName||"Context")+".Provider";case H:var i=n.render;return n=n.displayName,n||(n=i.displayName||i.name||"",n=n!==""?"ForwardRef("+n+")":"ForwardRef"),n;case Z:return i=n.displayName||null,i!==null?i:re(n.type)||"Memo";case ue:i=n._payload,n=n._init;try{return re(n(i))}catch{}}return null}function _e(n){var i=n.type;switch(n.tag){case 24:return"Cache";case 9:return(i.displayName||"Context")+".Consumer";case 10:return(i._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return n=i.render,n=n.displayName||n.name||"",i.displayName||(n!==""?"ForwardRef("+n+")":"ForwardRef");case 7:return"Fragment";case 5:return i;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return re(i);case 8:return i===E?"StrictMode":"Mode";case 22:return"Offscreen";case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if(typeof i=="function")return i.displayName||i.name||null;if(typeof i=="string")return i}return null}function me(n){switch(typeof n){case"boolean":case"number":case"string":case"undefined":return n;case"object":return n;default:return""}}function Fe(n){var i=n.type;return(n=n.nodeName)&&n.toLowerCase()==="input"&&(i==="checkbox"||i==="radio")}function Je(n){var i=Fe(n)?"checked":"value",a=Object.getOwnPropertyDescriptor(n.constructor.prototype,i),c=""+n[i];if(!n.hasOwnProperty(i)&&typeof a<"u"&&typeof a.get=="function"&&typeof a.set=="function"){var h=a.get,g=a.set;return Object.defineProperty(n,i,{configurable:!0,get:function(){return h.call(this)},set:function(T){c=""+T,g.call(this,T)}}),Object.defineProperty(n,i,{enumerable:a.enumerable}),{getValue:function(){return c},setValue:function(T){c=""+T},stopTracking:function(){n._valueTracker=null,delete n[i]}}}}function et(n){n._valueTracker||(n._valueTracker=Je(n))}function Wt(n){if(!n)return!1;var i=n._valueTracker;if(!i)return!0;var a=i.getValue(),c="";return n&&(c=Fe(n)?n.checked?"true":"false":n.value),n=c,n!==a?(i.setValue(n),!0):!1}function ft(n){if(n=n||(typeof document<"u"?document:void 0),typeof n>"u")return null;try{return n.activeElement||n.body}catch{return n.body}}function Nt(n,i){var a=i.checked;return le({},i,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:a??n._wrapperState.initialChecked})}function Mt(n,i){var a=i.defaultValue==null?"":i.defaultValue,c=i.checked!=null?i.checked:i.defaultChecked;a=me(i.value!=null?i.value:a),n._wrapperState={initialChecked:c,initialValue:a,controlled:i.type==="checkbox"||i.type==="radio"?i.checked!=null:i.value!=null}}function _t(n,i){i=i.checked,i!=null&&U(n,"checked",i,!1)}function Xt(n,i){_t(n,i);var a=me(i.value),c=i.type;if(a!=null)c==="number"?(a===0&&n.value===""||n.value!=a)&&(n.value=""+a):n.value!==""+a&&(n.value=""+a);else if(c==="submit"||c==="reset"){n.removeAttribute("value");return}i.hasOwnProperty("value")?nn(n,i.type,a):i.hasOwnProperty("defaultValue")&&nn(n,i.type,me(i.defaultValue)),i.checked==null&&i.defaultChecked!=null&&(n.defaultChecked=!!i.defaultChecked)}function tn(n,i,a){if(i.hasOwnProperty("value")||i.hasOwnProperty("defaultValue")){var c=i.type;if(!(c!=="submit"&&c!=="reset"||i.value!==void 0&&i.value!==null))return;i=""+n._wrapperState.initialValue,a||i===n.value||(n.value=i),n.defaultValue=i}a=n.name,a!==""&&(n.name=""),n.defaultChecked=!!n._wrapperState.initialChecked,a!==""&&(n.name=a)}function nn(n,i,a){(i!=="number"||ft(n.ownerDocument)!==n)&&(a==null?n.defaultValue=""+n._wrapperState.initialValue:n.defaultValue!==""+a&&(n.defaultValue=""+a))}var Kt=Array.isArray;function It(n,i,a,c){if(n=n.options,i){i={};for(var h=0;h<a.length;h++)i["$"+a[h]]=!0;for(a=0;a<n.length;a++)h=i.hasOwnProperty("$"+n[a].value),n[a].selected!==h&&(n[a].selected=h),h&&c&&(n[a].defaultSelected=!0)}else{for(a=""+me(a),i=null,h=0;h<n.length;h++){if(n[h].value===a){n[h].selected=!0,c&&(n[h].defaultSelected=!0);return}i!==null||n[h].disabled||(i=n[h])}i!==null&&(i.selected=!0)}}function qt(n,i){if(i.dangerouslySetInnerHTML!=null)throw Error(t(91));return le({},i,{value:void 0,defaultValue:void 0,children:""+n._wrapperState.initialValue})}function W(n,i){var a=i.value;if(a==null){if(a=i.children,i=i.defaultValue,a!=null){if(i!=null)throw Error(t(92));if(Kt(a)){if(1<a.length)throw Error(t(93));a=a[0]}i=a}i==null&&(i=""),a=i}n._wrapperState={initialValue:me(a)}}function _n(n,i){var a=me(i.value),c=me(i.defaultValue);a!=null&&(a=""+a,a!==n.value&&(n.value=a),i.defaultValue==null&&n.defaultValue!==a&&(n.defaultValue=a)),c!=null&&(n.defaultValue=""+c)}function Tt(n){var i=n.textContent;i===n._wrapperState.initialValue&&i!==""&&i!==null&&(n.value=i)}function F(n){switch(n){case"svg":return"http://www.w3.org/2000/svg";case"math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}function b(n,i){return n==null||n==="http://www.w3.org/1999/xhtml"?F(i):n==="http://www.w3.org/2000/svg"&&i==="foreignObject"?"http://www.w3.org/1999/xhtml":n}var $,ie=(function(n){return typeof MSApp<"u"&&MSApp.execUnsafeLocalFunction?function(i,a,c,h){MSApp.execUnsafeLocalFunction(function(){return n(i,a,c,h)})}:n})(function(n,i){if(n.namespaceURI!=="http://www.w3.org/2000/svg"||"innerHTML"in n)n.innerHTML=i;else{for($=$||document.createElement("div"),$.innerHTML="<svg>"+i.valueOf().toString()+"</svg>",i=$.firstChild;n.firstChild;)n.removeChild(n.firstChild);for(;i.firstChild;)n.appendChild(i.firstChild)}});function de(n,i){if(i){var a=n.firstChild;if(a&&a===n.lastChild&&a.nodeType===3){a.nodeValue=i;return}}n.textContent=i}var be={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},Ne=["Webkit","ms","Moz","O"];Object.keys(be).forEach(function(n){Ne.forEach(function(i){i=i+n.charAt(0).toUpperCase()+n.substring(1),be[i]=be[n]})});function fe(n,i,a){return i==null||typeof i=="boolean"||i===""?"":a||typeof i!="number"||i===0||be.hasOwnProperty(n)&&be[n]?(""+i).trim():i+"px"}function ge(n,i){n=n.style;for(var a in i)if(i.hasOwnProperty(a)){var c=a.indexOf("--")===0,h=fe(a,i[a],c);a==="float"&&(a="cssFloat"),c?n.setProperty(a,h):n[a]=h}}var Pe=le({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});function qe(n,i){if(i){if(Pe[n]&&(i.children!=null||i.dangerouslySetInnerHTML!=null))throw Error(t(137,n));if(i.dangerouslySetInnerHTML!=null){if(i.children!=null)throw Error(t(60));if(typeof i.dangerouslySetInnerHTML!="object"||!("__html"in i.dangerouslySetInnerHTML))throw Error(t(61))}if(i.style!=null&&typeof i.style!="object")throw Error(t(62))}}function Le(n,i){if(n.indexOf("-")===-1)return typeof i.is=="string";switch(n){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Ce=null;function Qe(n){return n=n.target||n.srcElement||window,n.correspondingUseElement&&(n=n.correspondingUseElement),n.nodeType===3?n.parentNode:n}var tt=null,at=null,j=null;function Ae(n){if(n=qa(n)){if(typeof tt!="function")throw Error(t(280));var i=n.stateNode;i&&(i=Ko(i),tt(n.stateNode,n.type,i))}}function pe(n){at?j?j.push(n):j=[n]:at=n}function Re(){if(at){var n=at,i=j;if(j=at=null,Ae(n),i)for(n=0;n<i.length;n++)Ae(i[n])}}function Ie(n,i){return n(i)}function ve(){}var Ge=!1;function He(n,i,a){if(Ge)return n(i,a);Ge=!0;try{return Ie(n,i,a)}finally{Ge=!1,(at!==null||j!==null)&&(ve(),Re())}}function kt(n,i){var a=n.stateNode;if(a===null)return null;var c=Ko(a);if(c===null)return null;a=c[i];e:switch(i){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(c=!c.disabled)||(n=n.type,c=!(n==="button"||n==="input"||n==="select"||n==="textarea")),n=!c;break e;default:n=!1}if(n)return null;if(a&&typeof a!="function")throw Error(t(231,i,typeof a));return a}var Rt=!1;if(f)try{var Tn={};Object.defineProperty(Tn,"passive",{get:function(){Rt=!0}}),window.addEventListener("test",Tn,Tn),window.removeEventListener("test",Tn,Tn)}catch{Rt=!1}function ri(n,i,a,c,h,g,T,O,V){var oe=Array.prototype.slice.call(arguments,3);try{i.apply(a,oe)}catch(Se){this.onError(Se)}}var $r=!1,Ts=null,Kr=!1,Zr=null,Fc={onError:function(n){$r=!0,Ts=n}};function Lo(n,i,a,c,h,g,T,O,V){$r=!1,Ts=null,ri.apply(Fc,arguments)}function Io(n,i,a,c,h,g,T,O,V){if(Lo.apply(this,arguments),$r){if($r){var oe=Ts;$r=!1,Ts=null}else throw Error(t(198));Kr||(Kr=!0,Zr=oe)}}function Un(n){var i=n,a=n;if(n.alternate)for(;i.return;)i=i.return;else{n=i;do i=n,(i.flags&4098)!==0&&(a=i.return),n=i.return;while(n)}return i.tag===3?a:null}function As(n){if(n.tag===13){var i=n.memoizedState;if(i===null&&(n=n.alternate,n!==null&&(i=n.memoizedState)),i!==null)return i.dehydrated}return null}function Aa(n){if(Un(n)!==n)throw Error(t(188))}function Do(n){var i=n.alternate;if(!i){if(i=Un(n),i===null)throw Error(t(188));return i!==n?null:n}for(var a=n,c=i;;){var h=a.return;if(h===null)break;var g=h.alternate;if(g===null){if(c=h.return,c!==null){a=c;continue}break}if(h.child===g.child){for(g=h.child;g;){if(g===a)return Aa(h),n;if(g===c)return Aa(h),i;g=g.sibling}throw Error(t(188))}if(a.return!==c.return)a=h,c=g;else{for(var T=!1,O=h.child;O;){if(O===a){T=!0,a=h,c=g;break}if(O===c){T=!0,c=h,a=g;break}O=O.sibling}if(!T){for(O=g.child;O;){if(O===a){T=!0,a=g,c=h;break}if(O===c){T=!0,c=g,a=h;break}O=O.sibling}if(!T)throw Error(t(189))}}if(a.alternate!==c)throw Error(t(190))}if(a.tag!==3)throw Error(t(188));return a.stateNode.current===a?n:i}function Qr(n){return n=Do(n),n!==null?Ca(n):null}function Ca(n){if(n.tag===5||n.tag===6)return n;for(n=n.child;n!==null;){var i=Ca(n);if(i!==null)return i;n=n.sibling}return null}var Jr=e.unstable_scheduleCallback,Na=e.unstable_cancelCallback,Uo=e.unstable_shouldYield,kc=e.unstable_requestPaint,Zt=e.unstable_now,Oc=e.unstable_getCurrentPriorityLevel,Ra=e.unstable_ImmediatePriority,C=e.unstable_UserBlockingPriority,X=e.unstable_NormalPriority,ae=e.unstable_LowPriority,te=e.unstable_IdlePriority,ee=null,Te=null;function ze(n){if(Te&&typeof Te.onCommitFiberRoot=="function")try{Te.onCommitFiberRoot(ee,n,void 0,(n.current.flags&128)===128)}catch{}}var we=Math.clz32?Math.clz32:lt,We=Math.log,Ze=Math.LN2;function lt(n){return n>>>=0,n===0?32:31-(We(n)/Ze|0)|0}var ct=64,Ye=4194304;function bt(n){switch(n&-n){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return n&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;default:return n}}function Ot(n,i){var a=n.pendingLanes;if(a===0)return 0;var c=0,h=n.suspendedLanes,g=n.pingedLanes,T=a&268435455;if(T!==0){var O=T&~h;O!==0?c=bt(O):(g&=T,g!==0&&(c=bt(g)))}else T=a&~h,T!==0?c=bt(T):g!==0&&(c=bt(g));if(c===0)return 0;if(i!==0&&i!==c&&(i&h)===0&&(h=c&-c,g=i&-i,h>=g||h===16&&(g&4194240)!==0))return i;if((c&4)!==0&&(c|=a&16),i=n.entangledLanes,i!==0)for(n=n.entanglements,i&=c;0<i;)a=31-we(i),h=1<<a,c|=n[a],i&=~h;return c}function Yt(n,i){switch(n){case 1:case 2:case 4:return i+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return i+5e3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function Dt(n,i){for(var a=n.suspendedLanes,c=n.pingedLanes,h=n.expirationTimes,g=n.pendingLanes;0<g;){var T=31-we(g),O=1<<T,V=h[T];V===-1?((O&a)===0||(O&c)!==0)&&(h[T]=Yt(O,i)):V<=i&&(n.expiredLanes|=O),g&=~O}}function on(n){return n=n.pendingLanes&-1073741825,n!==0?n:n&1073741824?1073741824:0}function ke(){var n=ct;return ct<<=1,(ct&4194240)===0&&(ct=64),n}function yn(n){for(var i=[],a=0;31>a;a++)i.push(n);return i}function mt(n,i,a){n.pendingLanes|=i,i!==536870912&&(n.suspendedLanes=0,n.pingedLanes=0),n=n.eventTimes,i=31-we(i),n[i]=a}function Hn(n,i){var a=n.pendingLanes&~i;n.pendingLanes=i,n.suspendedLanes=0,n.pingedLanes=0,n.expiredLanes&=i,n.mutableReadLanes&=i,n.entangledLanes&=i,i=n.entanglements;var c=n.eventTimes;for(n=n.expirationTimes;0<a;){var h=31-we(a),g=1<<h;i[h]=0,c[h]=-1,n[h]=-1,a&=~g}}function jn(n,i){var a=n.entangledLanes|=i;for(n=n.entanglements;a;){var c=31-we(a),h=1<<c;h&i|n[c]&i&&(n[c]|=i),a&=~h}}var gt=0;function Gi(n){return n&=-n,1<n?4<n?(n&268435455)!==0?16:536870912:4:1}var Pt,Vt,gi,Ut,xi,Ri=!1,es=[],gr=null,xr=null,vr=null,Pa=new Map,La=new Map,_r=[],t0="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");function yh(n,i){switch(n){case"focusin":case"focusout":gr=null;break;case"dragenter":case"dragleave":xr=null;break;case"mouseover":case"mouseout":vr=null;break;case"pointerover":case"pointerout":Pa.delete(i.pointerId);break;case"gotpointercapture":case"lostpointercapture":La.delete(i.pointerId)}}function Ia(n,i,a,c,h,g){return n===null||n.nativeEvent!==g?(n={blockedOn:i,domEventName:a,eventSystemFlags:c,nativeEvent:g,targetContainers:[h]},i!==null&&(i=qa(i),i!==null&&Vt(i)),n):(n.eventSystemFlags|=c,i=n.targetContainers,h!==null&&i.indexOf(h)===-1&&i.push(h),n)}function n0(n,i,a,c,h){switch(i){case"focusin":return gr=Ia(gr,n,i,a,c,h),!0;case"dragenter":return xr=Ia(xr,n,i,a,c,h),!0;case"mouseover":return vr=Ia(vr,n,i,a,c,h),!0;case"pointerover":var g=h.pointerId;return Pa.set(g,Ia(Pa.get(g)||null,n,i,a,c,h)),!0;case"gotpointercapture":return g=h.pointerId,La.set(g,Ia(La.get(g)||null,n,i,a,c,h)),!0}return!1}function Sh(n){var i=ts(n.target);if(i!==null){var a=Un(i);if(a!==null){if(i=a.tag,i===13){if(i=As(a),i!==null){n.blockedOn=i,xi(n.priority,function(){gi(a)});return}}else if(i===3&&a.stateNode.current.memoizedState.isDehydrated){n.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}n.blockedOn=null}function Fo(n){if(n.blockedOn!==null)return!1;for(var i=n.targetContainers;0<i.length;){var a=Bc(n.domEventName,n.eventSystemFlags,i[0],n.nativeEvent);if(a===null){a=n.nativeEvent;var c=new a.constructor(a.type,a);Ce=c,a.target.dispatchEvent(c),Ce=null}else return i=qa(a),i!==null&&Vt(i),n.blockedOn=a,!1;i.shift()}return!0}function Mh(n,i,a){Fo(n)&&a.delete(i)}function i0(){Ri=!1,gr!==null&&Fo(gr)&&(gr=null),xr!==null&&Fo(xr)&&(xr=null),vr!==null&&Fo(vr)&&(vr=null),Pa.forEach(Mh),La.forEach(Mh)}function Da(n,i){n.blockedOn===i&&(n.blockedOn=null,Ri||(Ri=!0,e.unstable_scheduleCallback(e.unstable_NormalPriority,i0)))}function Ua(n){function i(h){return Da(h,n)}if(0<es.length){Da(es[0],n);for(var a=1;a<es.length;a++){var c=es[a];c.blockedOn===n&&(c.blockedOn=null)}}for(gr!==null&&Da(gr,n),xr!==null&&Da(xr,n),vr!==null&&Da(vr,n),Pa.forEach(i),La.forEach(i),a=0;a<_r.length;a++)c=_r[a],c.blockedOn===n&&(c.blockedOn=null);for(;0<_r.length&&(a=_r[0],a.blockedOn===null);)Sh(a),a.blockedOn===null&&_r.shift()}var Cs=N.ReactCurrentBatchConfig,ko=!0;function r0(n,i,a,c){var h=gt,g=Cs.transition;Cs.transition=null;try{gt=1,zc(n,i,a,c)}finally{gt=h,Cs.transition=g}}function s0(n,i,a,c){var h=gt,g=Cs.transition;Cs.transition=null;try{gt=4,zc(n,i,a,c)}finally{gt=h,Cs.transition=g}}function zc(n,i,a,c){if(ko){var h=Bc(n,i,a,c);if(h===null)iu(n,i,c,Oo,a),yh(n,c);else if(n0(h,n,i,a,c))c.stopPropagation();else if(yh(n,c),i&4&&-1<t0.indexOf(n)){for(;h!==null;){var g=qa(h);if(g!==null&&Pt(g),g=Bc(n,i,a,c),g===null&&iu(n,i,c,Oo,a),g===h)break;h=g}h!==null&&c.stopPropagation()}else iu(n,i,c,null,a)}}var Oo=null;function Bc(n,i,a,c){if(Oo=null,n=Qe(c),n=ts(n),n!==null)if(i=Un(n),i===null)n=null;else if(a=i.tag,a===13){if(n=As(i),n!==null)return n;n=null}else if(a===3){if(i.stateNode.current.memoizedState.isDehydrated)return i.tag===3?i.stateNode.containerInfo:null;n=null}else i!==n&&(n=null);return Oo=n,null}function bh(n){switch(n){case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 1;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"toggle":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 4;case"message":switch(Oc()){case Ra:return 1;case C:return 4;case X:case ae:return 16;case te:return 536870912;default:return 16}default:return 16}}var yr=null,Vc=null,zo=null;function Eh(){if(zo)return zo;var n,i=Vc,a=i.length,c,h="value"in yr?yr.value:yr.textContent,g=h.length;for(n=0;n<a&&i[n]===h[n];n++);var T=a-n;for(c=1;c<=T&&i[a-c]===h[g-c];c++);return zo=h.slice(n,1<c?1-c:void 0)}function Bo(n){var i=n.keyCode;return"charCode"in n?(n=n.charCode,n===0&&i===13&&(n=13)):n=i,n===10&&(n=13),32<=n||n===13?n:0}function Vo(){return!0}function wh(){return!1}function Qn(n){function i(a,c,h,g,T){this._reactName=a,this._targetInst=h,this.type=c,this.nativeEvent=g,this.target=T,this.currentTarget=null;for(var O in n)n.hasOwnProperty(O)&&(a=n[O],this[O]=a?a(g):g[O]);return this.isDefaultPrevented=(g.defaultPrevented!=null?g.defaultPrevented:g.returnValue===!1)?Vo:wh,this.isPropagationStopped=wh,this}return le(i.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=Vo)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=Vo)},persist:function(){},isPersistent:Vo}),i}var Ns={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(n){return n.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Hc=Qn(Ns),Fa=le({},Ns,{view:0,detail:0}),a0=Qn(Fa),jc,Gc,ka,Ho=le({},Fa,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Xc,button:0,buttons:0,relatedTarget:function(n){return n.relatedTarget===void 0?n.fromElement===n.srcElement?n.toElement:n.fromElement:n.relatedTarget},movementX:function(n){return"movementX"in n?n.movementX:(n!==ka&&(ka&&n.type==="mousemove"?(jc=n.screenX-ka.screenX,Gc=n.screenY-ka.screenY):Gc=jc=0,ka=n),jc)},movementY:function(n){return"movementY"in n?n.movementY:Gc}}),Th=Qn(Ho),o0=le({},Ho,{dataTransfer:0}),l0=Qn(o0),c0=le({},Fa,{relatedTarget:0}),Wc=Qn(c0),u0=le({},Ns,{animationName:0,elapsedTime:0,pseudoElement:0}),d0=Qn(u0),f0=le({},Ns,{clipboardData:function(n){return"clipboardData"in n?n.clipboardData:window.clipboardData}}),h0=Qn(f0),p0=le({},Ns,{data:0}),Ah=Qn(p0),m0={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},g0={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},x0={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function v0(n){var i=this.nativeEvent;return i.getModifierState?i.getModifierState(n):(n=x0[n])?!!i[n]:!1}function Xc(){return v0}var _0=le({},Fa,{key:function(n){if(n.key){var i=m0[n.key]||n.key;if(i!=="Unidentified")return i}return n.type==="keypress"?(n=Bo(n),n===13?"Enter":String.fromCharCode(n)):n.type==="keydown"||n.type==="keyup"?g0[n.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Xc,charCode:function(n){return n.type==="keypress"?Bo(n):0},keyCode:function(n){return n.type==="keydown"||n.type==="keyup"?n.keyCode:0},which:function(n){return n.type==="keypress"?Bo(n):n.type==="keydown"||n.type==="keyup"?n.keyCode:0}}),y0=Qn(_0),S0=le({},Ho,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Ch=Qn(S0),M0=le({},Fa,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Xc}),b0=Qn(M0),E0=le({},Ns,{propertyName:0,elapsedTime:0,pseudoElement:0}),w0=Qn(E0),T0=le({},Ho,{deltaX:function(n){return"deltaX"in n?n.deltaX:"wheelDeltaX"in n?-n.wheelDeltaX:0},deltaY:function(n){return"deltaY"in n?n.deltaY:"wheelDeltaY"in n?-n.wheelDeltaY:"wheelDelta"in n?-n.wheelDelta:0},deltaZ:0,deltaMode:0}),A0=Qn(T0),C0=[9,13,27,32],qc=f&&"CompositionEvent"in window,Oa=null;f&&"documentMode"in document&&(Oa=document.documentMode);var N0=f&&"TextEvent"in window&&!Oa,Nh=f&&(!qc||Oa&&8<Oa&&11>=Oa),Rh=" ",Ph=!1;function Lh(n,i){switch(n){case"keyup":return C0.indexOf(i.keyCode)!==-1;case"keydown":return i.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Ih(n){return n=n.detail,typeof n=="object"&&"data"in n?n.data:null}var Rs=!1;function R0(n,i){switch(n){case"compositionend":return Ih(i);case"keypress":return i.which!==32?null:(Ph=!0,Rh);case"textInput":return n=i.data,n===Rh&&Ph?null:n;default:return null}}function P0(n,i){if(Rs)return n==="compositionend"||!qc&&Lh(n,i)?(n=Eh(),zo=Vc=yr=null,Rs=!1,n):null;switch(n){case"paste":return null;case"keypress":if(!(i.ctrlKey||i.altKey||i.metaKey)||i.ctrlKey&&i.altKey){if(i.char&&1<i.char.length)return i.char;if(i.which)return String.fromCharCode(i.which)}return null;case"compositionend":return Nh&&i.locale!=="ko"?null:i.data;default:return null}}var L0={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Dh(n){var i=n&&n.nodeName&&n.nodeName.toLowerCase();return i==="input"?!!L0[n.type]:i==="textarea"}function Uh(n,i,a,c){pe(c),i=qo(i,"onChange"),0<i.length&&(a=new Hc("onChange","change",null,a,c),n.push({event:a,listeners:i}))}var za=null,Ba=null;function I0(n){Jh(n,0)}function jo(n){var i=Us(n);if(Wt(i))return n}function D0(n,i){if(n==="change")return i}var Fh=!1;if(f){var Yc;if(f){var $c="oninput"in document;if(!$c){var kh=document.createElement("div");kh.setAttribute("oninput","return;"),$c=typeof kh.oninput=="function"}Yc=$c}else Yc=!1;Fh=Yc&&(!document.documentMode||9<document.documentMode)}function Oh(){za&&(za.detachEvent("onpropertychange",zh),Ba=za=null)}function zh(n){if(n.propertyName==="value"&&jo(Ba)){var i=[];Uh(i,Ba,n,Qe(n)),He(I0,i)}}function U0(n,i,a){n==="focusin"?(Oh(),za=i,Ba=a,za.attachEvent("onpropertychange",zh)):n==="focusout"&&Oh()}function F0(n){if(n==="selectionchange"||n==="keyup"||n==="keydown")return jo(Ba)}function k0(n,i){if(n==="click")return jo(i)}function O0(n,i){if(n==="input"||n==="change")return jo(i)}function z0(n,i){return n===i&&(n!==0||1/n===1/i)||n!==n&&i!==i}var vi=typeof Object.is=="function"?Object.is:z0;function Va(n,i){if(vi(n,i))return!0;if(typeof n!="object"||n===null||typeof i!="object"||i===null)return!1;var a=Object.keys(n),c=Object.keys(i);if(a.length!==c.length)return!1;for(c=0;c<a.length;c++){var h=a[c];if(!p.call(i,h)||!vi(n[h],i[h]))return!1}return!0}function Bh(n){for(;n&&n.firstChild;)n=n.firstChild;return n}function Vh(n,i){var a=Bh(n);n=0;for(var c;a;){if(a.nodeType===3){if(c=n+a.textContent.length,n<=i&&c>=i)return{node:a,offset:i-n};n=c}e:{for(;a;){if(a.nextSibling){a=a.nextSibling;break e}a=a.parentNode}a=void 0}a=Bh(a)}}function Hh(n,i){return n&&i?n===i?!0:n&&n.nodeType===3?!1:i&&i.nodeType===3?Hh(n,i.parentNode):"contains"in n?n.contains(i):n.compareDocumentPosition?!!(n.compareDocumentPosition(i)&16):!1:!1}function jh(){for(var n=window,i=ft();i instanceof n.HTMLIFrameElement;){try{var a=typeof i.contentWindow.location.href=="string"}catch{a=!1}if(a)n=i.contentWindow;else break;i=ft(n.document)}return i}function Kc(n){var i=n&&n.nodeName&&n.nodeName.toLowerCase();return i&&(i==="input"&&(n.type==="text"||n.type==="search"||n.type==="tel"||n.type==="url"||n.type==="password")||i==="textarea"||n.contentEditable==="true")}function B0(n){var i=jh(),a=n.focusedElem,c=n.selectionRange;if(i!==a&&a&&a.ownerDocument&&Hh(a.ownerDocument.documentElement,a)){if(c!==null&&Kc(a)){if(i=c.start,n=c.end,n===void 0&&(n=i),"selectionStart"in a)a.selectionStart=i,a.selectionEnd=Math.min(n,a.value.length);else if(n=(i=a.ownerDocument||document)&&i.defaultView||window,n.getSelection){n=n.getSelection();var h=a.textContent.length,g=Math.min(c.start,h);c=c.end===void 0?g:Math.min(c.end,h),!n.extend&&g>c&&(h=c,c=g,g=h),h=Vh(a,g);var T=Vh(a,c);h&&T&&(n.rangeCount!==1||n.anchorNode!==h.node||n.anchorOffset!==h.offset||n.focusNode!==T.node||n.focusOffset!==T.offset)&&(i=i.createRange(),i.setStart(h.node,h.offset),n.removeAllRanges(),g>c?(n.addRange(i),n.extend(T.node,T.offset)):(i.setEnd(T.node,T.offset),n.addRange(i)))}}for(i=[],n=a;n=n.parentNode;)n.nodeType===1&&i.push({element:n,left:n.scrollLeft,top:n.scrollTop});for(typeof a.focus=="function"&&a.focus(),a=0;a<i.length;a++)n=i[a],n.element.scrollLeft=n.left,n.element.scrollTop=n.top}}var V0=f&&"documentMode"in document&&11>=document.documentMode,Ps=null,Zc=null,Ha=null,Qc=!1;function Gh(n,i,a){var c=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;Qc||Ps==null||Ps!==ft(c)||(c=Ps,"selectionStart"in c&&Kc(c)?c={start:c.selectionStart,end:c.selectionEnd}:(c=(c.ownerDocument&&c.ownerDocument.defaultView||window).getSelection(),c={anchorNode:c.anchorNode,anchorOffset:c.anchorOffset,focusNode:c.focusNode,focusOffset:c.focusOffset}),Ha&&Va(Ha,c)||(Ha=c,c=qo(Zc,"onSelect"),0<c.length&&(i=new Hc("onSelect","select",null,i,a),n.push({event:i,listeners:c}),i.target=Ps)))}function Go(n,i){var a={};return a[n.toLowerCase()]=i.toLowerCase(),a["Webkit"+n]="webkit"+i,a["Moz"+n]="moz"+i,a}var Ls={animationend:Go("Animation","AnimationEnd"),animationiteration:Go("Animation","AnimationIteration"),animationstart:Go("Animation","AnimationStart"),transitionend:Go("Transition","TransitionEnd")},Jc={},Wh={};f&&(Wh=document.createElement("div").style,"AnimationEvent"in window||(delete Ls.animationend.animation,delete Ls.animationiteration.animation,delete Ls.animationstart.animation),"TransitionEvent"in window||delete Ls.transitionend.transition);function Wo(n){if(Jc[n])return Jc[n];if(!Ls[n])return n;var i=Ls[n],a;for(a in i)if(i.hasOwnProperty(a)&&a in Wh)return Jc[n]=i[a];return n}var Xh=Wo("animationend"),qh=Wo("animationiteration"),Yh=Wo("animationstart"),$h=Wo("transitionend"),Kh=new Map,Zh="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");function Sr(n,i){Kh.set(n,i),l(i,[n])}for(var eu=0;eu<Zh.length;eu++){var tu=Zh[eu],H0=tu.toLowerCase(),j0=tu[0].toUpperCase()+tu.slice(1);Sr(H0,"on"+j0)}Sr(Xh,"onAnimationEnd"),Sr(qh,"onAnimationIteration"),Sr(Yh,"onAnimationStart"),Sr("dblclick","onDoubleClick"),Sr("focusin","onFocus"),Sr("focusout","onBlur"),Sr($h,"onTransitionEnd"),d("onMouseEnter",["mouseout","mouseover"]),d("onMouseLeave",["mouseout","mouseover"]),d("onPointerEnter",["pointerout","pointerover"]),d("onPointerLeave",["pointerout","pointerover"]),l("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),l("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),l("onBeforeInput",["compositionend","keypress","textInput","paste"]),l("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),l("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),l("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var ja="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),G0=new Set("cancel close invalid load scroll toggle".split(" ").concat(ja));function Qh(n,i,a){var c=n.type||"unknown-event";n.currentTarget=a,Io(c,i,void 0,n),n.currentTarget=null}function Jh(n,i){i=(i&4)!==0;for(var a=0;a<n.length;a++){var c=n[a],h=c.event;c=c.listeners;e:{var g=void 0;if(i)for(var T=c.length-1;0<=T;T--){var O=c[T],V=O.instance,oe=O.currentTarget;if(O=O.listener,V!==g&&h.isPropagationStopped())break e;Qh(h,O,oe),g=V}else for(T=0;T<c.length;T++){if(O=c[T],V=O.instance,oe=O.currentTarget,O=O.listener,V!==g&&h.isPropagationStopped())break e;Qh(h,O,oe),g=V}}}if(Kr)throw n=Zr,Kr=!1,Zr=null,n}function Ht(n,i){var a=i[cu];a===void 0&&(a=i[cu]=new Set);var c=n+"__bubble";a.has(c)||(ep(i,n,2,!1),a.add(c))}function nu(n,i,a){var c=0;i&&(c|=4),ep(a,n,c,i)}var Xo="_reactListening"+Math.random().toString(36).slice(2);function Ga(n){if(!n[Xo]){n[Xo]=!0,r.forEach(function(a){a!=="selectionchange"&&(G0.has(a)||nu(a,!1,n),nu(a,!0,n))});var i=n.nodeType===9?n:n.ownerDocument;i===null||i[Xo]||(i[Xo]=!0,nu("selectionchange",!1,i))}}function ep(n,i,a,c){switch(bh(i)){case 1:var h=r0;break;case 4:h=s0;break;default:h=zc}a=h.bind(null,i,a,n),h=void 0,!Rt||i!=="touchstart"&&i!=="touchmove"&&i!=="wheel"||(h=!0),c?h!==void 0?n.addEventListener(i,a,{capture:!0,passive:h}):n.addEventListener(i,a,!0):h!==void 0?n.addEventListener(i,a,{passive:h}):n.addEventListener(i,a,!1)}function iu(n,i,a,c,h){var g=c;if((i&1)===0&&(i&2)===0&&c!==null)e:for(;;){if(c===null)return;var T=c.tag;if(T===3||T===4){var O=c.stateNode.containerInfo;if(O===h||O.nodeType===8&&O.parentNode===h)break;if(T===4)for(T=c.return;T!==null;){var V=T.tag;if((V===3||V===4)&&(V=T.stateNode.containerInfo,V===h||V.nodeType===8&&V.parentNode===h))return;T=T.return}for(;O!==null;){if(T=ts(O),T===null)return;if(V=T.tag,V===5||V===6){c=g=T;continue e}O=O.parentNode}}c=c.return}He(function(){var oe=g,Se=Qe(a),Me=[];e:{var ye=Kh.get(n);if(ye!==void 0){var Oe=Hc,je=n;switch(n){case"keypress":if(Bo(a)===0)break e;case"keydown":case"keyup":Oe=y0;break;case"focusin":je="focus",Oe=Wc;break;case"focusout":je="blur",Oe=Wc;break;case"beforeblur":case"afterblur":Oe=Wc;break;case"click":if(a.button===2)break e;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":Oe=Th;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":Oe=l0;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":Oe=b0;break;case Xh:case qh:case Yh:Oe=d0;break;case $h:Oe=w0;break;case"scroll":Oe=a0;break;case"wheel":Oe=A0;break;case"copy":case"cut":case"paste":Oe=h0;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":Oe=Ch}var Xe=(i&4)!==0,an=!Xe&&n==="scroll",J=Xe?ye!==null?ye+"Capture":null:ye;Xe=[];for(var G=oe,ne;G!==null;){ne=G;var Ee=ne.stateNode;if(ne.tag===5&&Ee!==null&&(ne=Ee,J!==null&&(Ee=kt(G,J),Ee!=null&&Xe.push(Wa(G,Ee,ne)))),an)break;G=G.return}0<Xe.length&&(ye=new Oe(ye,je,null,a,Se),Me.push({event:ye,listeners:Xe}))}}if((i&7)===0){e:{if(ye=n==="mouseover"||n==="pointerover",Oe=n==="mouseout"||n==="pointerout",ye&&a!==Ce&&(je=a.relatedTarget||a.fromElement)&&(ts(je)||je[Wi]))break e;if((Oe||ye)&&(ye=Se.window===Se?Se:(ye=Se.ownerDocument)?ye.defaultView||ye.parentWindow:window,Oe?(je=a.relatedTarget||a.toElement,Oe=oe,je=je?ts(je):null,je!==null&&(an=Un(je),je!==an||je.tag!==5&&je.tag!==6)&&(je=null)):(Oe=null,je=oe),Oe!==je)){if(Xe=Th,Ee="onMouseLeave",J="onMouseEnter",G="mouse",(n==="pointerout"||n==="pointerover")&&(Xe=Ch,Ee="onPointerLeave",J="onPointerEnter",G="pointer"),an=Oe==null?ye:Us(Oe),ne=je==null?ye:Us(je),ye=new Xe(Ee,G+"leave",Oe,a,Se),ye.target=an,ye.relatedTarget=ne,Ee=null,ts(Se)===oe&&(Xe=new Xe(J,G+"enter",je,a,Se),Xe.target=ne,Xe.relatedTarget=an,Ee=Xe),an=Ee,Oe&&je)t:{for(Xe=Oe,J=je,G=0,ne=Xe;ne;ne=Is(ne))G++;for(ne=0,Ee=J;Ee;Ee=Is(Ee))ne++;for(;0<G-ne;)Xe=Is(Xe),G--;for(;0<ne-G;)J=Is(J),ne--;for(;G--;){if(Xe===J||J!==null&&Xe===J.alternate)break t;Xe=Is(Xe),J=Is(J)}Xe=null}else Xe=null;Oe!==null&&tp(Me,ye,Oe,Xe,!1),je!==null&&an!==null&&tp(Me,an,je,Xe,!0)}}e:{if(ye=oe?Us(oe):window,Oe=ye.nodeName&&ye.nodeName.toLowerCase(),Oe==="select"||Oe==="input"&&ye.type==="file")var Ke=D0;else if(Dh(ye))if(Fh)Ke=O0;else{Ke=F0;var nt=U0}else(Oe=ye.nodeName)&&Oe.toLowerCase()==="input"&&(ye.type==="checkbox"||ye.type==="radio")&&(Ke=k0);if(Ke&&(Ke=Ke(n,oe))){Uh(Me,Ke,a,Se);break e}nt&&nt(n,ye,oe),n==="focusout"&&(nt=ye._wrapperState)&&nt.controlled&&ye.type==="number"&&nn(ye,"number",ye.value)}switch(nt=oe?Us(oe):window,n){case"focusin":(Dh(nt)||nt.contentEditable==="true")&&(Ps=nt,Zc=oe,Ha=null);break;case"focusout":Ha=Zc=Ps=null;break;case"mousedown":Qc=!0;break;case"contextmenu":case"mouseup":case"dragend":Qc=!1,Gh(Me,a,Se);break;case"selectionchange":if(V0)break;case"keydown":case"keyup":Gh(Me,a,Se)}var it;if(qc)e:{switch(n){case"compositionstart":var ot="onCompositionStart";break e;case"compositionend":ot="onCompositionEnd";break e;case"compositionupdate":ot="onCompositionUpdate";break e}ot=void 0}else Rs?Lh(n,a)&&(ot="onCompositionEnd"):n==="keydown"&&a.keyCode===229&&(ot="onCompositionStart");ot&&(Nh&&a.locale!=="ko"&&(Rs||ot!=="onCompositionStart"?ot==="onCompositionEnd"&&Rs&&(it=Eh()):(yr=Se,Vc="value"in yr?yr.value:yr.textContent,Rs=!0)),nt=qo(oe,ot),0<nt.length&&(ot=new Ah(ot,n,null,a,Se),Me.push({event:ot,listeners:nt}),it?ot.data=it:(it=Ih(a),it!==null&&(ot.data=it)))),(it=N0?R0(n,a):P0(n,a))&&(oe=qo(oe,"onBeforeInput"),0<oe.length&&(Se=new Ah("onBeforeInput","beforeinput",null,a,Se),Me.push({event:Se,listeners:oe}),Se.data=it))}Jh(Me,i)})}function Wa(n,i,a){return{instance:n,listener:i,currentTarget:a}}function qo(n,i){for(var a=i+"Capture",c=[];n!==null;){var h=n,g=h.stateNode;h.tag===5&&g!==null&&(h=g,g=kt(n,a),g!=null&&c.unshift(Wa(n,g,h)),g=kt(n,i),g!=null&&c.push(Wa(n,g,h))),n=n.return}return c}function Is(n){if(n===null)return null;do n=n.return;while(n&&n.tag!==5);return n||null}function tp(n,i,a,c,h){for(var g=i._reactName,T=[];a!==null&&a!==c;){var O=a,V=O.alternate,oe=O.stateNode;if(V!==null&&V===c)break;O.tag===5&&oe!==null&&(O=oe,h?(V=kt(a,g),V!=null&&T.unshift(Wa(a,V,O))):h||(V=kt(a,g),V!=null&&T.push(Wa(a,V,O)))),a=a.return}T.length!==0&&n.push({event:i,listeners:T})}var W0=/\r\n?/g,X0=/\u0000|\uFFFD/g;function np(n){return(typeof n=="string"?n:""+n).replace(W0,`
`).replace(X0,"")}function Yo(n,i,a){if(i=np(i),np(n)!==i&&a)throw Error(t(425))}function $o(){}var ru=null,su=null;function au(n,i){return n==="textarea"||n==="noscript"||typeof i.children=="string"||typeof i.children=="number"||typeof i.dangerouslySetInnerHTML=="object"&&i.dangerouslySetInnerHTML!==null&&i.dangerouslySetInnerHTML.__html!=null}var ou=typeof setTimeout=="function"?setTimeout:void 0,q0=typeof clearTimeout=="function"?clearTimeout:void 0,ip=typeof Promise=="function"?Promise:void 0,Y0=typeof queueMicrotask=="function"?queueMicrotask:typeof ip<"u"?function(n){return ip.resolve(null).then(n).catch($0)}:ou;function $0(n){setTimeout(function(){throw n})}function lu(n,i){var a=i,c=0;do{var h=a.nextSibling;if(n.removeChild(a),h&&h.nodeType===8)if(a=h.data,a==="/$"){if(c===0){n.removeChild(h),Ua(i);return}c--}else a!=="$"&&a!=="$?"&&a!=="$!"||c++;a=h}while(a);Ua(i)}function Mr(n){for(;n!=null;n=n.nextSibling){var i=n.nodeType;if(i===1||i===3)break;if(i===8){if(i=n.data,i==="$"||i==="$!"||i==="$?")break;if(i==="/$")return null}}return n}function rp(n){n=n.previousSibling;for(var i=0;n;){if(n.nodeType===8){var a=n.data;if(a==="$"||a==="$!"||a==="$?"){if(i===0)return n;i--}else a==="/$"&&i++}n=n.previousSibling}return null}var Ds=Math.random().toString(36).slice(2),Pi="__reactFiber$"+Ds,Xa="__reactProps$"+Ds,Wi="__reactContainer$"+Ds,cu="__reactEvents$"+Ds,K0="__reactListeners$"+Ds,Z0="__reactHandles$"+Ds;function ts(n){var i=n[Pi];if(i)return i;for(var a=n.parentNode;a;){if(i=a[Wi]||a[Pi]){if(a=i.alternate,i.child!==null||a!==null&&a.child!==null)for(n=rp(n);n!==null;){if(a=n[Pi])return a;n=rp(n)}return i}n=a,a=n.parentNode}return null}function qa(n){return n=n[Pi]||n[Wi],!n||n.tag!==5&&n.tag!==6&&n.tag!==13&&n.tag!==3?null:n}function Us(n){if(n.tag===5||n.tag===6)return n.stateNode;throw Error(t(33))}function Ko(n){return n[Xa]||null}var uu=[],Fs=-1;function br(n){return{current:n}}function jt(n){0>Fs||(n.current=uu[Fs],uu[Fs]=null,Fs--)}function zt(n,i){Fs++,uu[Fs]=n.current,n.current=i}var Er={},An=br(Er),Gn=br(!1),ns=Er;function ks(n,i){var a=n.type.contextTypes;if(!a)return Er;var c=n.stateNode;if(c&&c.__reactInternalMemoizedUnmaskedChildContext===i)return c.__reactInternalMemoizedMaskedChildContext;var h={},g;for(g in a)h[g]=i[g];return c&&(n=n.stateNode,n.__reactInternalMemoizedUnmaskedChildContext=i,n.__reactInternalMemoizedMaskedChildContext=h),h}function Wn(n){return n=n.childContextTypes,n!=null}function Zo(){jt(Gn),jt(An)}function sp(n,i,a){if(An.current!==Er)throw Error(t(168));zt(An,i),zt(Gn,a)}function ap(n,i,a){var c=n.stateNode;if(i=i.childContextTypes,typeof c.getChildContext!="function")return a;c=c.getChildContext();for(var h in c)if(!(h in i))throw Error(t(108,_e(n)||"Unknown",h));return le({},a,c)}function Qo(n){return n=(n=n.stateNode)&&n.__reactInternalMemoizedMergedChildContext||Er,ns=An.current,zt(An,n),zt(Gn,Gn.current),!0}function op(n,i,a){var c=n.stateNode;if(!c)throw Error(t(169));a?(n=ap(n,i,ns),c.__reactInternalMemoizedMergedChildContext=n,jt(Gn),jt(An),zt(An,n)):jt(Gn),zt(Gn,a)}var Xi=null,Jo=!1,du=!1;function lp(n){Xi===null?Xi=[n]:Xi.push(n)}function Q0(n){Jo=!0,lp(n)}function wr(){if(!du&&Xi!==null){du=!0;var n=0,i=gt;try{var a=Xi;for(gt=1;n<a.length;n++){var c=a[n];do c=c(!0);while(c!==null)}Xi=null,Jo=!1}catch(h){throw Xi!==null&&(Xi=Xi.slice(n+1)),Jr(Ra,wr),h}finally{gt=i,du=!1}}return null}var Os=[],zs=0,el=null,tl=0,si=[],ai=0,is=null,qi=1,Yi="";function rs(n,i){Os[zs++]=tl,Os[zs++]=el,el=n,tl=i}function cp(n,i,a){si[ai++]=qi,si[ai++]=Yi,si[ai++]=is,is=n;var c=qi;n=Yi;var h=32-we(c)-1;c&=~(1<<h),a+=1;var g=32-we(i)+h;if(30<g){var T=h-h%5;g=(c&(1<<T)-1).toString(32),c>>=T,h-=T,qi=1<<32-we(i)+h|a<<h|c,Yi=g+n}else qi=1<<g|a<<h|c,Yi=n}function fu(n){n.return!==null&&(rs(n,1),cp(n,1,0))}function hu(n){for(;n===el;)el=Os[--zs],Os[zs]=null,tl=Os[--zs],Os[zs]=null;for(;n===is;)is=si[--ai],si[ai]=null,Yi=si[--ai],si[ai]=null,qi=si[--ai],si[ai]=null}var Jn=null,ei=null,$t=!1,_i=null;function up(n,i){var a=ui(5,null,null,0);a.elementType="DELETED",a.stateNode=i,a.return=n,i=n.deletions,i===null?(n.deletions=[a],n.flags|=16):i.push(a)}function dp(n,i){switch(n.tag){case 5:var a=n.type;return i=i.nodeType!==1||a.toLowerCase()!==i.nodeName.toLowerCase()?null:i,i!==null?(n.stateNode=i,Jn=n,ei=Mr(i.firstChild),!0):!1;case 6:return i=n.pendingProps===""||i.nodeType!==3?null:i,i!==null?(n.stateNode=i,Jn=n,ei=null,!0):!1;case 13:return i=i.nodeType!==8?null:i,i!==null?(a=is!==null?{id:qi,overflow:Yi}:null,n.memoizedState={dehydrated:i,treeContext:a,retryLane:1073741824},a=ui(18,null,null,0),a.stateNode=i,a.return=n,n.child=a,Jn=n,ei=null,!0):!1;default:return!1}}function pu(n){return(n.mode&1)!==0&&(n.flags&128)===0}function mu(n){if($t){var i=ei;if(i){var a=i;if(!dp(n,i)){if(pu(n))throw Error(t(418));i=Mr(a.nextSibling);var c=Jn;i&&dp(n,i)?up(c,a):(n.flags=n.flags&-4097|2,$t=!1,Jn=n)}}else{if(pu(n))throw Error(t(418));n.flags=n.flags&-4097|2,$t=!1,Jn=n}}}function fp(n){for(n=n.return;n!==null&&n.tag!==5&&n.tag!==3&&n.tag!==13;)n=n.return;Jn=n}function nl(n){if(n!==Jn)return!1;if(!$t)return fp(n),$t=!0,!1;var i;if((i=n.tag!==3)&&!(i=n.tag!==5)&&(i=n.type,i=i!=="head"&&i!=="body"&&!au(n.type,n.memoizedProps)),i&&(i=ei)){if(pu(n))throw hp(),Error(t(418));for(;i;)up(n,i),i=Mr(i.nextSibling)}if(fp(n),n.tag===13){if(n=n.memoizedState,n=n!==null?n.dehydrated:null,!n)throw Error(t(317));e:{for(n=n.nextSibling,i=0;n;){if(n.nodeType===8){var a=n.data;if(a==="/$"){if(i===0){ei=Mr(n.nextSibling);break e}i--}else a!=="$"&&a!=="$!"&&a!=="$?"||i++}n=n.nextSibling}ei=null}}else ei=Jn?Mr(n.stateNode.nextSibling):null;return!0}function hp(){for(var n=ei;n;)n=Mr(n.nextSibling)}function Bs(){ei=Jn=null,$t=!1}function gu(n){_i===null?_i=[n]:_i.push(n)}var J0=N.ReactCurrentBatchConfig;function Ya(n,i,a){if(n=a.ref,n!==null&&typeof n!="function"&&typeof n!="object"){if(a._owner){if(a=a._owner,a){if(a.tag!==1)throw Error(t(309));var c=a.stateNode}if(!c)throw Error(t(147,n));var h=c,g=""+n;return i!==null&&i.ref!==null&&typeof i.ref=="function"&&i.ref._stringRef===g?i.ref:(i=function(T){var O=h.refs;T===null?delete O[g]:O[g]=T},i._stringRef=g,i)}if(typeof n!="string")throw Error(t(284));if(!a._owner)throw Error(t(290,n))}return n}function il(n,i){throw n=Object.prototype.toString.call(i),Error(t(31,n==="[object Object]"?"object with keys {"+Object.keys(i).join(", ")+"}":n))}function pp(n){var i=n._init;return i(n._payload)}function mp(n){function i(J,G){if(n){var ne=J.deletions;ne===null?(J.deletions=[G],J.flags|=16):ne.push(G)}}function a(J,G){if(!n)return null;for(;G!==null;)i(J,G),G=G.sibling;return null}function c(J,G){for(J=new Map;G!==null;)G.key!==null?J.set(G.key,G):J.set(G.index,G),G=G.sibling;return J}function h(J,G){return J=Ir(J,G),J.index=0,J.sibling=null,J}function g(J,G,ne){return J.index=ne,n?(ne=J.alternate,ne!==null?(ne=ne.index,ne<G?(J.flags|=2,G):ne):(J.flags|=2,G)):(J.flags|=1048576,G)}function T(J){return n&&J.alternate===null&&(J.flags|=2),J}function O(J,G,ne,Ee){return G===null||G.tag!==6?(G=od(ne,J.mode,Ee),G.return=J,G):(G=h(G,ne),G.return=J,G)}function V(J,G,ne,Ee){var Ke=ne.type;return Ke===D?Se(J,G,ne.props.children,Ee,ne.key):G!==null&&(G.elementType===Ke||typeof Ke=="object"&&Ke!==null&&Ke.$$typeof===ue&&pp(Ke)===G.type)?(Ee=h(G,ne.props),Ee.ref=Ya(J,G,ne),Ee.return=J,Ee):(Ee=Al(ne.type,ne.key,ne.props,null,J.mode,Ee),Ee.ref=Ya(J,G,ne),Ee.return=J,Ee)}function oe(J,G,ne,Ee){return G===null||G.tag!==4||G.stateNode.containerInfo!==ne.containerInfo||G.stateNode.implementation!==ne.implementation?(G=ld(ne,J.mode,Ee),G.return=J,G):(G=h(G,ne.children||[]),G.return=J,G)}function Se(J,G,ne,Ee,Ke){return G===null||G.tag!==7?(G=fs(ne,J.mode,Ee,Ke),G.return=J,G):(G=h(G,ne),G.return=J,G)}function Me(J,G,ne){if(typeof G=="string"&&G!==""||typeof G=="number")return G=od(""+G,J.mode,ne),G.return=J,G;if(typeof G=="object"&&G!==null){switch(G.$$typeof){case L:return ne=Al(G.type,G.key,G.props,null,J.mode,ne),ne.ref=Ya(J,null,G),ne.return=J,ne;case R:return G=ld(G,J.mode,ne),G.return=J,G;case ue:var Ee=G._init;return Me(J,Ee(G._payload),ne)}if(Kt(G)||se(G))return G=fs(G,J.mode,ne,null),G.return=J,G;il(J,G)}return null}function ye(J,G,ne,Ee){var Ke=G!==null?G.key:null;if(typeof ne=="string"&&ne!==""||typeof ne=="number")return Ke!==null?null:O(J,G,""+ne,Ee);if(typeof ne=="object"&&ne!==null){switch(ne.$$typeof){case L:return ne.key===Ke?V(J,G,ne,Ee):null;case R:return ne.key===Ke?oe(J,G,ne,Ee):null;case ue:return Ke=ne._init,ye(J,G,Ke(ne._payload),Ee)}if(Kt(ne)||se(ne))return Ke!==null?null:Se(J,G,ne,Ee,null);il(J,ne)}return null}function Oe(J,G,ne,Ee,Ke){if(typeof Ee=="string"&&Ee!==""||typeof Ee=="number")return J=J.get(ne)||null,O(G,J,""+Ee,Ke);if(typeof Ee=="object"&&Ee!==null){switch(Ee.$$typeof){case L:return J=J.get(Ee.key===null?ne:Ee.key)||null,V(G,J,Ee,Ke);case R:return J=J.get(Ee.key===null?ne:Ee.key)||null,oe(G,J,Ee,Ke);case ue:var nt=Ee._init;return Oe(J,G,ne,nt(Ee._payload),Ke)}if(Kt(Ee)||se(Ee))return J=J.get(ne)||null,Se(G,J,Ee,Ke,null);il(G,Ee)}return null}function je(J,G,ne,Ee){for(var Ke=null,nt=null,it=G,ot=G=0,xn=null;it!==null&&ot<ne.length;ot++){it.index>ot?(xn=it,it=null):xn=it.sibling;var At=ye(J,it,ne[ot],Ee);if(At===null){it===null&&(it=xn);break}n&&it&&At.alternate===null&&i(J,it),G=g(At,G,ot),nt===null?Ke=At:nt.sibling=At,nt=At,it=xn}if(ot===ne.length)return a(J,it),$t&&rs(J,ot),Ke;if(it===null){for(;ot<ne.length;ot++)it=Me(J,ne[ot],Ee),it!==null&&(G=g(it,G,ot),nt===null?Ke=it:nt.sibling=it,nt=it);return $t&&rs(J,ot),Ke}for(it=c(J,it);ot<ne.length;ot++)xn=Oe(it,J,ot,ne[ot],Ee),xn!==null&&(n&&xn.alternate!==null&&it.delete(xn.key===null?ot:xn.key),G=g(xn,G,ot),nt===null?Ke=xn:nt.sibling=xn,nt=xn);return n&&it.forEach(function(Dr){return i(J,Dr)}),$t&&rs(J,ot),Ke}function Xe(J,G,ne,Ee){var Ke=se(ne);if(typeof Ke!="function")throw Error(t(150));if(ne=Ke.call(ne),ne==null)throw Error(t(151));for(var nt=Ke=null,it=G,ot=G=0,xn=null,At=ne.next();it!==null&&!At.done;ot++,At=ne.next()){it.index>ot?(xn=it,it=null):xn=it.sibling;var Dr=ye(J,it,At.value,Ee);if(Dr===null){it===null&&(it=xn);break}n&&it&&Dr.alternate===null&&i(J,it),G=g(Dr,G,ot),nt===null?Ke=Dr:nt.sibling=Dr,nt=Dr,it=xn}if(At.done)return a(J,it),$t&&rs(J,ot),Ke;if(it===null){for(;!At.done;ot++,At=ne.next())At=Me(J,At.value,Ee),At!==null&&(G=g(At,G,ot),nt===null?Ke=At:nt.sibling=At,nt=At);return $t&&rs(J,ot),Ke}for(it=c(J,it);!At.done;ot++,At=ne.next())At=Oe(it,J,ot,At.value,Ee),At!==null&&(n&&At.alternate!==null&&it.delete(At.key===null?ot:At.key),G=g(At,G,ot),nt===null?Ke=At:nt.sibling=At,nt=At);return n&&it.forEach(function(Lv){return i(J,Lv)}),$t&&rs(J,ot),Ke}function an(J,G,ne,Ee){if(typeof ne=="object"&&ne!==null&&ne.type===D&&ne.key===null&&(ne=ne.props.children),typeof ne=="object"&&ne!==null){switch(ne.$$typeof){case L:e:{for(var Ke=ne.key,nt=G;nt!==null;){if(nt.key===Ke){if(Ke=ne.type,Ke===D){if(nt.tag===7){a(J,nt.sibling),G=h(nt,ne.props.children),G.return=J,J=G;break e}}else if(nt.elementType===Ke||typeof Ke=="object"&&Ke!==null&&Ke.$$typeof===ue&&pp(Ke)===nt.type){a(J,nt.sibling),G=h(nt,ne.props),G.ref=Ya(J,nt,ne),G.return=J,J=G;break e}a(J,nt);break}else i(J,nt);nt=nt.sibling}ne.type===D?(G=fs(ne.props.children,J.mode,Ee,ne.key),G.return=J,J=G):(Ee=Al(ne.type,ne.key,ne.props,null,J.mode,Ee),Ee.ref=Ya(J,G,ne),Ee.return=J,J=Ee)}return T(J);case R:e:{for(nt=ne.key;G!==null;){if(G.key===nt)if(G.tag===4&&G.stateNode.containerInfo===ne.containerInfo&&G.stateNode.implementation===ne.implementation){a(J,G.sibling),G=h(G,ne.children||[]),G.return=J,J=G;break e}else{a(J,G);break}else i(J,G);G=G.sibling}G=ld(ne,J.mode,Ee),G.return=J,J=G}return T(J);case ue:return nt=ne._init,an(J,G,nt(ne._payload),Ee)}if(Kt(ne))return je(J,G,ne,Ee);if(se(ne))return Xe(J,G,ne,Ee);il(J,ne)}return typeof ne=="string"&&ne!==""||typeof ne=="number"?(ne=""+ne,G!==null&&G.tag===6?(a(J,G.sibling),G=h(G,ne),G.return=J,J=G):(a(J,G),G=od(ne,J.mode,Ee),G.return=J,J=G),T(J)):a(J,G)}return an}var Vs=mp(!0),gp=mp(!1),rl=br(null),sl=null,Hs=null,xu=null;function vu(){xu=Hs=sl=null}function _u(n){var i=rl.current;jt(rl),n._currentValue=i}function yu(n,i,a){for(;n!==null;){var c=n.alternate;if((n.childLanes&i)!==i?(n.childLanes|=i,c!==null&&(c.childLanes|=i)):c!==null&&(c.childLanes&i)!==i&&(c.childLanes|=i),n===a)break;n=n.return}}function js(n,i){sl=n,xu=Hs=null,n=n.dependencies,n!==null&&n.firstContext!==null&&((n.lanes&i)!==0&&(Xn=!0),n.firstContext=null)}function oi(n){var i=n._currentValue;if(xu!==n)if(n={context:n,memoizedValue:i,next:null},Hs===null){if(sl===null)throw Error(t(308));Hs=n,sl.dependencies={lanes:0,firstContext:n}}else Hs=Hs.next=n;return i}var ss=null;function Su(n){ss===null?ss=[n]:ss.push(n)}function xp(n,i,a,c){var h=i.interleaved;return h===null?(a.next=a,Su(i)):(a.next=h.next,h.next=a),i.interleaved=a,$i(n,c)}function $i(n,i){n.lanes|=i;var a=n.alternate;for(a!==null&&(a.lanes|=i),a=n,n=n.return;n!==null;)n.childLanes|=i,a=n.alternate,a!==null&&(a.childLanes|=i),a=n,n=n.return;return a.tag===3?a.stateNode:null}var Tr=!1;function Mu(n){n.updateQueue={baseState:n.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}function vp(n,i){n=n.updateQueue,i.updateQueue===n&&(i.updateQueue={baseState:n.baseState,firstBaseUpdate:n.firstBaseUpdate,lastBaseUpdate:n.lastBaseUpdate,shared:n.shared,effects:n.effects})}function Ki(n,i){return{eventTime:n,lane:i,tag:0,payload:null,callback:null,next:null}}function Ar(n,i,a){var c=n.updateQueue;if(c===null)return null;if(c=c.shared,(Et&2)!==0){var h=c.pending;return h===null?i.next=i:(i.next=h.next,h.next=i),c.pending=i,$i(n,a)}return h=c.interleaved,h===null?(i.next=i,Su(c)):(i.next=h.next,h.next=i),c.interleaved=i,$i(n,a)}function al(n,i,a){if(i=i.updateQueue,i!==null&&(i=i.shared,(a&4194240)!==0)){var c=i.lanes;c&=n.pendingLanes,a|=c,i.lanes=a,jn(n,a)}}function _p(n,i){var a=n.updateQueue,c=n.alternate;if(c!==null&&(c=c.updateQueue,a===c)){var h=null,g=null;if(a=a.firstBaseUpdate,a!==null){do{var T={eventTime:a.eventTime,lane:a.lane,tag:a.tag,payload:a.payload,callback:a.callback,next:null};g===null?h=g=T:g=g.next=T,a=a.next}while(a!==null);g===null?h=g=i:g=g.next=i}else h=g=i;a={baseState:c.baseState,firstBaseUpdate:h,lastBaseUpdate:g,shared:c.shared,effects:c.effects},n.updateQueue=a;return}n=a.lastBaseUpdate,n===null?a.firstBaseUpdate=i:n.next=i,a.lastBaseUpdate=i}function ol(n,i,a,c){var h=n.updateQueue;Tr=!1;var g=h.firstBaseUpdate,T=h.lastBaseUpdate,O=h.shared.pending;if(O!==null){h.shared.pending=null;var V=O,oe=V.next;V.next=null,T===null?g=oe:T.next=oe,T=V;var Se=n.alternate;Se!==null&&(Se=Se.updateQueue,O=Se.lastBaseUpdate,O!==T&&(O===null?Se.firstBaseUpdate=oe:O.next=oe,Se.lastBaseUpdate=V))}if(g!==null){var Me=h.baseState;T=0,Se=oe=V=null,O=g;do{var ye=O.lane,Oe=O.eventTime;if((c&ye)===ye){Se!==null&&(Se=Se.next={eventTime:Oe,lane:0,tag:O.tag,payload:O.payload,callback:O.callback,next:null});e:{var je=n,Xe=O;switch(ye=i,Oe=a,Xe.tag){case 1:if(je=Xe.payload,typeof je=="function"){Me=je.call(Oe,Me,ye);break e}Me=je;break e;case 3:je.flags=je.flags&-65537|128;case 0:if(je=Xe.payload,ye=typeof je=="function"?je.call(Oe,Me,ye):je,ye==null)break e;Me=le({},Me,ye);break e;case 2:Tr=!0}}O.callback!==null&&O.lane!==0&&(n.flags|=64,ye=h.effects,ye===null?h.effects=[O]:ye.push(O))}else Oe={eventTime:Oe,lane:ye,tag:O.tag,payload:O.payload,callback:O.callback,next:null},Se===null?(oe=Se=Oe,V=Me):Se=Se.next=Oe,T|=ye;if(O=O.next,O===null){if(O=h.shared.pending,O===null)break;ye=O,O=ye.next,ye.next=null,h.lastBaseUpdate=ye,h.shared.pending=null}}while(!0);if(Se===null&&(V=Me),h.baseState=V,h.firstBaseUpdate=oe,h.lastBaseUpdate=Se,i=h.shared.interleaved,i!==null){h=i;do T|=h.lane,h=h.next;while(h!==i)}else g===null&&(h.shared.lanes=0);ls|=T,n.lanes=T,n.memoizedState=Me}}function yp(n,i,a){if(n=i.effects,i.effects=null,n!==null)for(i=0;i<n.length;i++){var c=n[i],h=c.callback;if(h!==null){if(c.callback=null,c=a,typeof h!="function")throw Error(t(191,h));h.call(c)}}}var $a={},Li=br($a),Ka=br($a),Za=br($a);function as(n){if(n===$a)throw Error(t(174));return n}function bu(n,i){switch(zt(Za,i),zt(Ka,n),zt(Li,$a),n=i.nodeType,n){case 9:case 11:i=(i=i.documentElement)?i.namespaceURI:b(null,"");break;default:n=n===8?i.parentNode:i,i=n.namespaceURI||null,n=n.tagName,i=b(i,n)}jt(Li),zt(Li,i)}function Gs(){jt(Li),jt(Ka),jt(Za)}function Sp(n){as(Za.current);var i=as(Li.current),a=b(i,n.type);i!==a&&(zt(Ka,n),zt(Li,a))}function Eu(n){Ka.current===n&&(jt(Li),jt(Ka))}var Qt=br(0);function ll(n){for(var i=n;i!==null;){if(i.tag===13){var a=i.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||a.data==="$?"||a.data==="$!"))return i}else if(i.tag===19&&i.memoizedProps.revealOrder!==void 0){if((i.flags&128)!==0)return i}else if(i.child!==null){i.child.return=i,i=i.child;continue}if(i===n)break;for(;i.sibling===null;){if(i.return===null||i.return===n)return null;i=i.return}i.sibling.return=i.return,i=i.sibling}return null}var wu=[];function Tu(){for(var n=0;n<wu.length;n++)wu[n]._workInProgressVersionPrimary=null;wu.length=0}var cl=N.ReactCurrentDispatcher,Au=N.ReactCurrentBatchConfig,os=0,Jt=null,un=null,mn=null,ul=!1,Qa=!1,Ja=0,ev=0;function Cn(){throw Error(t(321))}function Cu(n,i){if(i===null)return!1;for(var a=0;a<i.length&&a<n.length;a++)if(!vi(n[a],i[a]))return!1;return!0}function Nu(n,i,a,c,h,g){if(os=g,Jt=i,i.memoizedState=null,i.updateQueue=null,i.lanes=0,cl.current=n===null||n.memoizedState===null?rv:sv,n=a(c,h),Qa){g=0;do{if(Qa=!1,Ja=0,25<=g)throw Error(t(301));g+=1,mn=un=null,i.updateQueue=null,cl.current=av,n=a(c,h)}while(Qa)}if(cl.current=hl,i=un!==null&&un.next!==null,os=0,mn=un=Jt=null,ul=!1,i)throw Error(t(300));return n}function Ru(){var n=Ja!==0;return Ja=0,n}function Ii(){var n={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return mn===null?Jt.memoizedState=mn=n:mn=mn.next=n,mn}function li(){if(un===null){var n=Jt.alternate;n=n!==null?n.memoizedState:null}else n=un.next;var i=mn===null?Jt.memoizedState:mn.next;if(i!==null)mn=i,un=n;else{if(n===null)throw Error(t(310));un=n,n={memoizedState:un.memoizedState,baseState:un.baseState,baseQueue:un.baseQueue,queue:un.queue,next:null},mn===null?Jt.memoizedState=mn=n:mn=mn.next=n}return mn}function eo(n,i){return typeof i=="function"?i(n):i}function Pu(n){var i=li(),a=i.queue;if(a===null)throw Error(t(311));a.lastRenderedReducer=n;var c=un,h=c.baseQueue,g=a.pending;if(g!==null){if(h!==null){var T=h.next;h.next=g.next,g.next=T}c.baseQueue=h=g,a.pending=null}if(h!==null){g=h.next,c=c.baseState;var O=T=null,V=null,oe=g;do{var Se=oe.lane;if((os&Se)===Se)V!==null&&(V=V.next={lane:0,action:oe.action,hasEagerState:oe.hasEagerState,eagerState:oe.eagerState,next:null}),c=oe.hasEagerState?oe.eagerState:n(c,oe.action);else{var Me={lane:Se,action:oe.action,hasEagerState:oe.hasEagerState,eagerState:oe.eagerState,next:null};V===null?(O=V=Me,T=c):V=V.next=Me,Jt.lanes|=Se,ls|=Se}oe=oe.next}while(oe!==null&&oe!==g);V===null?T=c:V.next=O,vi(c,i.memoizedState)||(Xn=!0),i.memoizedState=c,i.baseState=T,i.baseQueue=V,a.lastRenderedState=c}if(n=a.interleaved,n!==null){h=n;do g=h.lane,Jt.lanes|=g,ls|=g,h=h.next;while(h!==n)}else h===null&&(a.lanes=0);return[i.memoizedState,a.dispatch]}function Lu(n){var i=li(),a=i.queue;if(a===null)throw Error(t(311));a.lastRenderedReducer=n;var c=a.dispatch,h=a.pending,g=i.memoizedState;if(h!==null){a.pending=null;var T=h=h.next;do g=n(g,T.action),T=T.next;while(T!==h);vi(g,i.memoizedState)||(Xn=!0),i.memoizedState=g,i.baseQueue===null&&(i.baseState=g),a.lastRenderedState=g}return[g,c]}function Mp(){}function bp(n,i){var a=Jt,c=li(),h=i(),g=!vi(c.memoizedState,h);if(g&&(c.memoizedState=h,Xn=!0),c=c.queue,Iu(Tp.bind(null,a,c,n),[n]),c.getSnapshot!==i||g||mn!==null&&mn.memoizedState.tag&1){if(a.flags|=2048,to(9,wp.bind(null,a,c,h,i),void 0,null),gn===null)throw Error(t(349));(os&30)!==0||Ep(a,i,h)}return h}function Ep(n,i,a){n.flags|=16384,n={getSnapshot:i,value:a},i=Jt.updateQueue,i===null?(i={lastEffect:null,stores:null},Jt.updateQueue=i,i.stores=[n]):(a=i.stores,a===null?i.stores=[n]:a.push(n))}function wp(n,i,a,c){i.value=a,i.getSnapshot=c,Ap(i)&&Cp(n)}function Tp(n,i,a){return a(function(){Ap(i)&&Cp(n)})}function Ap(n){var i=n.getSnapshot;n=n.value;try{var a=i();return!vi(n,a)}catch{return!0}}function Cp(n){var i=$i(n,1);i!==null&&bi(i,n,1,-1)}function Np(n){var i=Ii();return typeof n=="function"&&(n=n()),i.memoizedState=i.baseState=n,n={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:eo,lastRenderedState:n},i.queue=n,n=n.dispatch=iv.bind(null,Jt,n),[i.memoizedState,n]}function to(n,i,a,c){return n={tag:n,create:i,destroy:a,deps:c,next:null},i=Jt.updateQueue,i===null?(i={lastEffect:null,stores:null},Jt.updateQueue=i,i.lastEffect=n.next=n):(a=i.lastEffect,a===null?i.lastEffect=n.next=n:(c=a.next,a.next=n,n.next=c,i.lastEffect=n)),n}function Rp(){return li().memoizedState}function dl(n,i,a,c){var h=Ii();Jt.flags|=n,h.memoizedState=to(1|i,a,void 0,c===void 0?null:c)}function fl(n,i,a,c){var h=li();c=c===void 0?null:c;var g=void 0;if(un!==null){var T=un.memoizedState;if(g=T.destroy,c!==null&&Cu(c,T.deps)){h.memoizedState=to(i,a,g,c);return}}Jt.flags|=n,h.memoizedState=to(1|i,a,g,c)}function Pp(n,i){return dl(8390656,8,n,i)}function Iu(n,i){return fl(2048,8,n,i)}function Lp(n,i){return fl(4,2,n,i)}function Ip(n,i){return fl(4,4,n,i)}function Dp(n,i){if(typeof i=="function")return n=n(),i(n),function(){i(null)};if(i!=null)return n=n(),i.current=n,function(){i.current=null}}function Up(n,i,a){return a=a!=null?a.concat([n]):null,fl(4,4,Dp.bind(null,i,n),a)}function Du(){}function Fp(n,i){var a=li();i=i===void 0?null:i;var c=a.memoizedState;return c!==null&&i!==null&&Cu(i,c[1])?c[0]:(a.memoizedState=[n,i],n)}function kp(n,i){var a=li();i=i===void 0?null:i;var c=a.memoizedState;return c!==null&&i!==null&&Cu(i,c[1])?c[0]:(n=n(),a.memoizedState=[n,i],n)}function Op(n,i,a){return(os&21)===0?(n.baseState&&(n.baseState=!1,Xn=!0),n.memoizedState=a):(vi(a,i)||(a=ke(),Jt.lanes|=a,ls|=a,n.baseState=!0),i)}function tv(n,i){var a=gt;gt=a!==0&&4>a?a:4,n(!0);var c=Au.transition;Au.transition={};try{n(!1),i()}finally{gt=a,Au.transition=c}}function zp(){return li().memoizedState}function nv(n,i,a){var c=Pr(n);if(a={lane:c,action:a,hasEagerState:!1,eagerState:null,next:null},Bp(n))Vp(i,a);else if(a=xp(n,i,a,c),a!==null){var h=kn();bi(a,n,c,h),Hp(a,i,c)}}function iv(n,i,a){var c=Pr(n),h={lane:c,action:a,hasEagerState:!1,eagerState:null,next:null};if(Bp(n))Vp(i,h);else{var g=n.alternate;if(n.lanes===0&&(g===null||g.lanes===0)&&(g=i.lastRenderedReducer,g!==null))try{var T=i.lastRenderedState,O=g(T,a);if(h.hasEagerState=!0,h.eagerState=O,vi(O,T)){var V=i.interleaved;V===null?(h.next=h,Su(i)):(h.next=V.next,V.next=h),i.interleaved=h;return}}catch{}finally{}a=xp(n,i,h,c),a!==null&&(h=kn(),bi(a,n,c,h),Hp(a,i,c))}}function Bp(n){var i=n.alternate;return n===Jt||i!==null&&i===Jt}function Vp(n,i){Qa=ul=!0;var a=n.pending;a===null?i.next=i:(i.next=a.next,a.next=i),n.pending=i}function Hp(n,i,a){if((a&4194240)!==0){var c=i.lanes;c&=n.pendingLanes,a|=c,i.lanes=a,jn(n,a)}}var hl={readContext:oi,useCallback:Cn,useContext:Cn,useEffect:Cn,useImperativeHandle:Cn,useInsertionEffect:Cn,useLayoutEffect:Cn,useMemo:Cn,useReducer:Cn,useRef:Cn,useState:Cn,useDebugValue:Cn,useDeferredValue:Cn,useTransition:Cn,useMutableSource:Cn,useSyncExternalStore:Cn,useId:Cn,unstable_isNewReconciler:!1},rv={readContext:oi,useCallback:function(n,i){return Ii().memoizedState=[n,i===void 0?null:i],n},useContext:oi,useEffect:Pp,useImperativeHandle:function(n,i,a){return a=a!=null?a.concat([n]):null,dl(4194308,4,Dp.bind(null,i,n),a)},useLayoutEffect:function(n,i){return dl(4194308,4,n,i)},useInsertionEffect:function(n,i){return dl(4,2,n,i)},useMemo:function(n,i){var a=Ii();return i=i===void 0?null:i,n=n(),a.memoizedState=[n,i],n},useReducer:function(n,i,a){var c=Ii();return i=a!==void 0?a(i):i,c.memoizedState=c.baseState=i,n={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:n,lastRenderedState:i},c.queue=n,n=n.dispatch=nv.bind(null,Jt,n),[c.memoizedState,n]},useRef:function(n){var i=Ii();return n={current:n},i.memoizedState=n},useState:Np,useDebugValue:Du,useDeferredValue:function(n){return Ii().memoizedState=n},useTransition:function(){var n=Np(!1),i=n[0];return n=tv.bind(null,n[1]),Ii().memoizedState=n,[i,n]},useMutableSource:function(){},useSyncExternalStore:function(n,i,a){var c=Jt,h=Ii();if($t){if(a===void 0)throw Error(t(407));a=a()}else{if(a=i(),gn===null)throw Error(t(349));(os&30)!==0||Ep(c,i,a)}h.memoizedState=a;var g={value:a,getSnapshot:i};return h.queue=g,Pp(Tp.bind(null,c,g,n),[n]),c.flags|=2048,to(9,wp.bind(null,c,g,a,i),void 0,null),a},useId:function(){var n=Ii(),i=gn.identifierPrefix;if($t){var a=Yi,c=qi;a=(c&~(1<<32-we(c)-1)).toString(32)+a,i=":"+i+"R"+a,a=Ja++,0<a&&(i+="H"+a.toString(32)),i+=":"}else a=ev++,i=":"+i+"r"+a.toString(32)+":";return n.memoizedState=i},unstable_isNewReconciler:!1},sv={readContext:oi,useCallback:Fp,useContext:oi,useEffect:Iu,useImperativeHandle:Up,useInsertionEffect:Lp,useLayoutEffect:Ip,useMemo:kp,useReducer:Pu,useRef:Rp,useState:function(){return Pu(eo)},useDebugValue:Du,useDeferredValue:function(n){var i=li();return Op(i,un.memoizedState,n)},useTransition:function(){var n=Pu(eo)[0],i=li().memoizedState;return[n,i]},useMutableSource:Mp,useSyncExternalStore:bp,useId:zp,unstable_isNewReconciler:!1},av={readContext:oi,useCallback:Fp,useContext:oi,useEffect:Iu,useImperativeHandle:Up,useInsertionEffect:Lp,useLayoutEffect:Ip,useMemo:kp,useReducer:Lu,useRef:Rp,useState:function(){return Lu(eo)},useDebugValue:Du,useDeferredValue:function(n){var i=li();return un===null?i.memoizedState=n:Op(i,un.memoizedState,n)},useTransition:function(){var n=Lu(eo)[0],i=li().memoizedState;return[n,i]},useMutableSource:Mp,useSyncExternalStore:bp,useId:zp,unstable_isNewReconciler:!1};function yi(n,i){if(n&&n.defaultProps){i=le({},i),n=n.defaultProps;for(var a in n)i[a]===void 0&&(i[a]=n[a]);return i}return i}function Uu(n,i,a,c){i=n.memoizedState,a=a(c,i),a=a==null?i:le({},i,a),n.memoizedState=a,n.lanes===0&&(n.updateQueue.baseState=a)}var pl={isMounted:function(n){return(n=n._reactInternals)?Un(n)===n:!1},enqueueSetState:function(n,i,a){n=n._reactInternals;var c=kn(),h=Pr(n),g=Ki(c,h);g.payload=i,a!=null&&(g.callback=a),i=Ar(n,g,h),i!==null&&(bi(i,n,h,c),al(i,n,h))},enqueueReplaceState:function(n,i,a){n=n._reactInternals;var c=kn(),h=Pr(n),g=Ki(c,h);g.tag=1,g.payload=i,a!=null&&(g.callback=a),i=Ar(n,g,h),i!==null&&(bi(i,n,h,c),al(i,n,h))},enqueueForceUpdate:function(n,i){n=n._reactInternals;var a=kn(),c=Pr(n),h=Ki(a,c);h.tag=2,i!=null&&(h.callback=i),i=Ar(n,h,c),i!==null&&(bi(i,n,c,a),al(i,n,c))}};function jp(n,i,a,c,h,g,T){return n=n.stateNode,typeof n.shouldComponentUpdate=="function"?n.shouldComponentUpdate(c,g,T):i.prototype&&i.prototype.isPureReactComponent?!Va(a,c)||!Va(h,g):!0}function Gp(n,i,a){var c=!1,h=Er,g=i.contextType;return typeof g=="object"&&g!==null?g=oi(g):(h=Wn(i)?ns:An.current,c=i.contextTypes,g=(c=c!=null)?ks(n,h):Er),i=new i(a,g),n.memoizedState=i.state!==null&&i.state!==void 0?i.state:null,i.updater=pl,n.stateNode=i,i._reactInternals=n,c&&(n=n.stateNode,n.__reactInternalMemoizedUnmaskedChildContext=h,n.__reactInternalMemoizedMaskedChildContext=g),i}function Wp(n,i,a,c){n=i.state,typeof i.componentWillReceiveProps=="function"&&i.componentWillReceiveProps(a,c),typeof i.UNSAFE_componentWillReceiveProps=="function"&&i.UNSAFE_componentWillReceiveProps(a,c),i.state!==n&&pl.enqueueReplaceState(i,i.state,null)}function Fu(n,i,a,c){var h=n.stateNode;h.props=a,h.state=n.memoizedState,h.refs={},Mu(n);var g=i.contextType;typeof g=="object"&&g!==null?h.context=oi(g):(g=Wn(i)?ns:An.current,h.context=ks(n,g)),h.state=n.memoizedState,g=i.getDerivedStateFromProps,typeof g=="function"&&(Uu(n,i,g,a),h.state=n.memoizedState),typeof i.getDerivedStateFromProps=="function"||typeof h.getSnapshotBeforeUpdate=="function"||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(i=h.state,typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount(),i!==h.state&&pl.enqueueReplaceState(h,h.state,null),ol(n,a,h,c),h.state=n.memoizedState),typeof h.componentDidMount=="function"&&(n.flags|=4194308)}function Ws(n,i){try{var a="",c=i;do a+=Ve(c),c=c.return;while(c);var h=a}catch(g){h=`
Error generating stack: `+g.message+`
`+g.stack}return{value:n,source:i,stack:h,digest:null}}function ku(n,i,a){return{value:n,source:null,stack:a??null,digest:i??null}}function Ou(n,i){try{console.error(i.value)}catch(a){setTimeout(function(){throw a})}}var ov=typeof WeakMap=="function"?WeakMap:Map;function Xp(n,i,a){a=Ki(-1,a),a.tag=3,a.payload={element:null};var c=i.value;return a.callback=function(){Sl||(Sl=!0,Ju=c),Ou(n,i)},a}function qp(n,i,a){a=Ki(-1,a),a.tag=3;var c=n.type.getDerivedStateFromError;if(typeof c=="function"){var h=i.value;a.payload=function(){return c(h)},a.callback=function(){Ou(n,i)}}var g=n.stateNode;return g!==null&&typeof g.componentDidCatch=="function"&&(a.callback=function(){Ou(n,i),typeof c!="function"&&(Nr===null?Nr=new Set([this]):Nr.add(this));var T=i.stack;this.componentDidCatch(i.value,{componentStack:T!==null?T:""})}),a}function Yp(n,i,a){var c=n.pingCache;if(c===null){c=n.pingCache=new ov;var h=new Set;c.set(i,h)}else h=c.get(i),h===void 0&&(h=new Set,c.set(i,h));h.has(a)||(h.add(a),n=Sv.bind(null,n,i,a),i.then(n,n))}function $p(n){do{var i;if((i=n.tag===13)&&(i=n.memoizedState,i=i!==null?i.dehydrated!==null:!0),i)return n;n=n.return}while(n!==null);return null}function Kp(n,i,a,c,h){return(n.mode&1)===0?(n===i?n.flags|=65536:(n.flags|=128,a.flags|=131072,a.flags&=-52805,a.tag===1&&(a.alternate===null?a.tag=17:(i=Ki(-1,1),i.tag=2,Ar(a,i,1))),a.lanes|=1),n):(n.flags|=65536,n.lanes=h,n)}var lv=N.ReactCurrentOwner,Xn=!1;function Fn(n,i,a,c){i.child=n===null?gp(i,null,a,c):Vs(i,n.child,a,c)}function Zp(n,i,a,c,h){a=a.render;var g=i.ref;return js(i,h),c=Nu(n,i,a,c,g,h),a=Ru(),n!==null&&!Xn?(i.updateQueue=n.updateQueue,i.flags&=-2053,n.lanes&=~h,Zi(n,i,h)):($t&&a&&fu(i),i.flags|=1,Fn(n,i,c,h),i.child)}function Qp(n,i,a,c,h){if(n===null){var g=a.type;return typeof g=="function"&&!ad(g)&&g.defaultProps===void 0&&a.compare===null&&a.defaultProps===void 0?(i.tag=15,i.type=g,Jp(n,i,g,c,h)):(n=Al(a.type,null,c,i,i.mode,h),n.ref=i.ref,n.return=i,i.child=n)}if(g=n.child,(n.lanes&h)===0){var T=g.memoizedProps;if(a=a.compare,a=a!==null?a:Va,a(T,c)&&n.ref===i.ref)return Zi(n,i,h)}return i.flags|=1,n=Ir(g,c),n.ref=i.ref,n.return=i,i.child=n}function Jp(n,i,a,c,h){if(n!==null){var g=n.memoizedProps;if(Va(g,c)&&n.ref===i.ref)if(Xn=!1,i.pendingProps=c=g,(n.lanes&h)!==0)(n.flags&131072)!==0&&(Xn=!0);else return i.lanes=n.lanes,Zi(n,i,h)}return zu(n,i,a,c,h)}function em(n,i,a){var c=i.pendingProps,h=c.children,g=n!==null?n.memoizedState:null;if(c.mode==="hidden")if((i.mode&1)===0)i.memoizedState={baseLanes:0,cachePool:null,transitions:null},zt(qs,ti),ti|=a;else{if((a&1073741824)===0)return n=g!==null?g.baseLanes|a:a,i.lanes=i.childLanes=1073741824,i.memoizedState={baseLanes:n,cachePool:null,transitions:null},i.updateQueue=null,zt(qs,ti),ti|=n,null;i.memoizedState={baseLanes:0,cachePool:null,transitions:null},c=g!==null?g.baseLanes:a,zt(qs,ti),ti|=c}else g!==null?(c=g.baseLanes|a,i.memoizedState=null):c=a,zt(qs,ti),ti|=c;return Fn(n,i,h,a),i.child}function tm(n,i){var a=i.ref;(n===null&&a!==null||n!==null&&n.ref!==a)&&(i.flags|=512,i.flags|=2097152)}function zu(n,i,a,c,h){var g=Wn(a)?ns:An.current;return g=ks(i,g),js(i,h),a=Nu(n,i,a,c,g,h),c=Ru(),n!==null&&!Xn?(i.updateQueue=n.updateQueue,i.flags&=-2053,n.lanes&=~h,Zi(n,i,h)):($t&&c&&fu(i),i.flags|=1,Fn(n,i,a,h),i.child)}function nm(n,i,a,c,h){if(Wn(a)){var g=!0;Qo(i)}else g=!1;if(js(i,h),i.stateNode===null)gl(n,i),Gp(i,a,c),Fu(i,a,c,h),c=!0;else if(n===null){var T=i.stateNode,O=i.memoizedProps;T.props=O;var V=T.context,oe=a.contextType;typeof oe=="object"&&oe!==null?oe=oi(oe):(oe=Wn(a)?ns:An.current,oe=ks(i,oe));var Se=a.getDerivedStateFromProps,Me=typeof Se=="function"||typeof T.getSnapshotBeforeUpdate=="function";Me||typeof T.UNSAFE_componentWillReceiveProps!="function"&&typeof T.componentWillReceiveProps!="function"||(O!==c||V!==oe)&&Wp(i,T,c,oe),Tr=!1;var ye=i.memoizedState;T.state=ye,ol(i,c,T,h),V=i.memoizedState,O!==c||ye!==V||Gn.current||Tr?(typeof Se=="function"&&(Uu(i,a,Se,c),V=i.memoizedState),(O=Tr||jp(i,a,O,c,ye,V,oe))?(Me||typeof T.UNSAFE_componentWillMount!="function"&&typeof T.componentWillMount!="function"||(typeof T.componentWillMount=="function"&&T.componentWillMount(),typeof T.UNSAFE_componentWillMount=="function"&&T.UNSAFE_componentWillMount()),typeof T.componentDidMount=="function"&&(i.flags|=4194308)):(typeof T.componentDidMount=="function"&&(i.flags|=4194308),i.memoizedProps=c,i.memoizedState=V),T.props=c,T.state=V,T.context=oe,c=O):(typeof T.componentDidMount=="function"&&(i.flags|=4194308),c=!1)}else{T=i.stateNode,vp(n,i),O=i.memoizedProps,oe=i.type===i.elementType?O:yi(i.type,O),T.props=oe,Me=i.pendingProps,ye=T.context,V=a.contextType,typeof V=="object"&&V!==null?V=oi(V):(V=Wn(a)?ns:An.current,V=ks(i,V));var Oe=a.getDerivedStateFromProps;(Se=typeof Oe=="function"||typeof T.getSnapshotBeforeUpdate=="function")||typeof T.UNSAFE_componentWillReceiveProps!="function"&&typeof T.componentWillReceiveProps!="function"||(O!==Me||ye!==V)&&Wp(i,T,c,V),Tr=!1,ye=i.memoizedState,T.state=ye,ol(i,c,T,h);var je=i.memoizedState;O!==Me||ye!==je||Gn.current||Tr?(typeof Oe=="function"&&(Uu(i,a,Oe,c),je=i.memoizedState),(oe=Tr||jp(i,a,oe,c,ye,je,V)||!1)?(Se||typeof T.UNSAFE_componentWillUpdate!="function"&&typeof T.componentWillUpdate!="function"||(typeof T.componentWillUpdate=="function"&&T.componentWillUpdate(c,je,V),typeof T.UNSAFE_componentWillUpdate=="function"&&T.UNSAFE_componentWillUpdate(c,je,V)),typeof T.componentDidUpdate=="function"&&(i.flags|=4),typeof T.getSnapshotBeforeUpdate=="function"&&(i.flags|=1024)):(typeof T.componentDidUpdate!="function"||O===n.memoizedProps&&ye===n.memoizedState||(i.flags|=4),typeof T.getSnapshotBeforeUpdate!="function"||O===n.memoizedProps&&ye===n.memoizedState||(i.flags|=1024),i.memoizedProps=c,i.memoizedState=je),T.props=c,T.state=je,T.context=V,c=oe):(typeof T.componentDidUpdate!="function"||O===n.memoizedProps&&ye===n.memoizedState||(i.flags|=4),typeof T.getSnapshotBeforeUpdate!="function"||O===n.memoizedProps&&ye===n.memoizedState||(i.flags|=1024),c=!1)}return Bu(n,i,a,c,g,h)}function Bu(n,i,a,c,h,g){tm(n,i);var T=(i.flags&128)!==0;if(!c&&!T)return h&&op(i,a,!1),Zi(n,i,g);c=i.stateNode,lv.current=i;var O=T&&typeof a.getDerivedStateFromError!="function"?null:c.render();return i.flags|=1,n!==null&&T?(i.child=Vs(i,n.child,null,g),i.child=Vs(i,null,O,g)):Fn(n,i,O,g),i.memoizedState=c.state,h&&op(i,a,!0),i.child}function im(n){var i=n.stateNode;i.pendingContext?sp(n,i.pendingContext,i.pendingContext!==i.context):i.context&&sp(n,i.context,!1),bu(n,i.containerInfo)}function rm(n,i,a,c,h){return Bs(),gu(h),i.flags|=256,Fn(n,i,a,c),i.child}var Vu={dehydrated:null,treeContext:null,retryLane:0};function Hu(n){return{baseLanes:n,cachePool:null,transitions:null}}function sm(n,i,a){var c=i.pendingProps,h=Qt.current,g=!1,T=(i.flags&128)!==0,O;if((O=T)||(O=n!==null&&n.memoizedState===null?!1:(h&2)!==0),O?(g=!0,i.flags&=-129):(n===null||n.memoizedState!==null)&&(h|=1),zt(Qt,h&1),n===null)return mu(i),n=i.memoizedState,n!==null&&(n=n.dehydrated,n!==null)?((i.mode&1)===0?i.lanes=1:n.data==="$!"?i.lanes=8:i.lanes=1073741824,null):(T=c.children,n=c.fallback,g?(c=i.mode,g=i.child,T={mode:"hidden",children:T},(c&1)===0&&g!==null?(g.childLanes=0,g.pendingProps=T):g=Cl(T,c,0,null),n=fs(n,c,a,null),g.return=i,n.return=i,g.sibling=n,i.child=g,i.child.memoizedState=Hu(a),i.memoizedState=Vu,n):ju(i,T));if(h=n.memoizedState,h!==null&&(O=h.dehydrated,O!==null))return cv(n,i,T,c,O,h,a);if(g){g=c.fallback,T=i.mode,h=n.child,O=h.sibling;var V={mode:"hidden",children:c.children};return(T&1)===0&&i.child!==h?(c=i.child,c.childLanes=0,c.pendingProps=V,i.deletions=null):(c=Ir(h,V),c.subtreeFlags=h.subtreeFlags&14680064),O!==null?g=Ir(O,g):(g=fs(g,T,a,null),g.flags|=2),g.return=i,c.return=i,c.sibling=g,i.child=c,c=g,g=i.child,T=n.child.memoizedState,T=T===null?Hu(a):{baseLanes:T.baseLanes|a,cachePool:null,transitions:T.transitions},g.memoizedState=T,g.childLanes=n.childLanes&~a,i.memoizedState=Vu,c}return g=n.child,n=g.sibling,c=Ir(g,{mode:"visible",children:c.children}),(i.mode&1)===0&&(c.lanes=a),c.return=i,c.sibling=null,n!==null&&(a=i.deletions,a===null?(i.deletions=[n],i.flags|=16):a.push(n)),i.child=c,i.memoizedState=null,c}function ju(n,i){return i=Cl({mode:"visible",children:i},n.mode,0,null),i.return=n,n.child=i}function ml(n,i,a,c){return c!==null&&gu(c),Vs(i,n.child,null,a),n=ju(i,i.pendingProps.children),n.flags|=2,i.memoizedState=null,n}function cv(n,i,a,c,h,g,T){if(a)return i.flags&256?(i.flags&=-257,c=ku(Error(t(422))),ml(n,i,T,c)):i.memoizedState!==null?(i.child=n.child,i.flags|=128,null):(g=c.fallback,h=i.mode,c=Cl({mode:"visible",children:c.children},h,0,null),g=fs(g,h,T,null),g.flags|=2,c.return=i,g.return=i,c.sibling=g,i.child=c,(i.mode&1)!==0&&Vs(i,n.child,null,T),i.child.memoizedState=Hu(T),i.memoizedState=Vu,g);if((i.mode&1)===0)return ml(n,i,T,null);if(h.data==="$!"){if(c=h.nextSibling&&h.nextSibling.dataset,c)var O=c.dgst;return c=O,g=Error(t(419)),c=ku(g,c,void 0),ml(n,i,T,c)}if(O=(T&n.childLanes)!==0,Xn||O){if(c=gn,c!==null){switch(T&-T){case 4:h=2;break;case 16:h=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:h=32;break;case 536870912:h=268435456;break;default:h=0}h=(h&(c.suspendedLanes|T))!==0?0:h,h!==0&&h!==g.retryLane&&(g.retryLane=h,$i(n,h),bi(c,n,h,-1))}return sd(),c=ku(Error(t(421))),ml(n,i,T,c)}return h.data==="$?"?(i.flags|=128,i.child=n.child,i=Mv.bind(null,n),h._reactRetry=i,null):(n=g.treeContext,ei=Mr(h.nextSibling),Jn=i,$t=!0,_i=null,n!==null&&(si[ai++]=qi,si[ai++]=Yi,si[ai++]=is,qi=n.id,Yi=n.overflow,is=i),i=ju(i,c.children),i.flags|=4096,i)}function am(n,i,a){n.lanes|=i;var c=n.alternate;c!==null&&(c.lanes|=i),yu(n.return,i,a)}function Gu(n,i,a,c,h){var g=n.memoizedState;g===null?n.memoizedState={isBackwards:i,rendering:null,renderingStartTime:0,last:c,tail:a,tailMode:h}:(g.isBackwards=i,g.rendering=null,g.renderingStartTime=0,g.last=c,g.tail=a,g.tailMode=h)}function om(n,i,a){var c=i.pendingProps,h=c.revealOrder,g=c.tail;if(Fn(n,i,c.children,a),c=Qt.current,(c&2)!==0)c=c&1|2,i.flags|=128;else{if(n!==null&&(n.flags&128)!==0)e:for(n=i.child;n!==null;){if(n.tag===13)n.memoizedState!==null&&am(n,a,i);else if(n.tag===19)am(n,a,i);else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===i)break e;for(;n.sibling===null;){if(n.return===null||n.return===i)break e;n=n.return}n.sibling.return=n.return,n=n.sibling}c&=1}if(zt(Qt,c),(i.mode&1)===0)i.memoizedState=null;else switch(h){case"forwards":for(a=i.child,h=null;a!==null;)n=a.alternate,n!==null&&ll(n)===null&&(h=a),a=a.sibling;a=h,a===null?(h=i.child,i.child=null):(h=a.sibling,a.sibling=null),Gu(i,!1,h,a,g);break;case"backwards":for(a=null,h=i.child,i.child=null;h!==null;){if(n=h.alternate,n!==null&&ll(n)===null){i.child=h;break}n=h.sibling,h.sibling=a,a=h,h=n}Gu(i,!0,a,null,g);break;case"together":Gu(i,!1,null,null,void 0);break;default:i.memoizedState=null}return i.child}function gl(n,i){(i.mode&1)===0&&n!==null&&(n.alternate=null,i.alternate=null,i.flags|=2)}function Zi(n,i,a){if(n!==null&&(i.dependencies=n.dependencies),ls|=i.lanes,(a&i.childLanes)===0)return null;if(n!==null&&i.child!==n.child)throw Error(t(153));if(i.child!==null){for(n=i.child,a=Ir(n,n.pendingProps),i.child=a,a.return=i;n.sibling!==null;)n=n.sibling,a=a.sibling=Ir(n,n.pendingProps),a.return=i;a.sibling=null}return i.child}function uv(n,i,a){switch(i.tag){case 3:im(i),Bs();break;case 5:Sp(i);break;case 1:Wn(i.type)&&Qo(i);break;case 4:bu(i,i.stateNode.containerInfo);break;case 10:var c=i.type._context,h=i.memoizedProps.value;zt(rl,c._currentValue),c._currentValue=h;break;case 13:if(c=i.memoizedState,c!==null)return c.dehydrated!==null?(zt(Qt,Qt.current&1),i.flags|=128,null):(a&i.child.childLanes)!==0?sm(n,i,a):(zt(Qt,Qt.current&1),n=Zi(n,i,a),n!==null?n.sibling:null);zt(Qt,Qt.current&1);break;case 19:if(c=(a&i.childLanes)!==0,(n.flags&128)!==0){if(c)return om(n,i,a);i.flags|=128}if(h=i.memoizedState,h!==null&&(h.rendering=null,h.tail=null,h.lastEffect=null),zt(Qt,Qt.current),c)break;return null;case 22:case 23:return i.lanes=0,em(n,i,a)}return Zi(n,i,a)}var lm,Wu,cm,um;lm=function(n,i){for(var a=i.child;a!==null;){if(a.tag===5||a.tag===6)n.appendChild(a.stateNode);else if(a.tag!==4&&a.child!==null){a.child.return=a,a=a.child;continue}if(a===i)break;for(;a.sibling===null;){if(a.return===null||a.return===i)return;a=a.return}a.sibling.return=a.return,a=a.sibling}},Wu=function(){},cm=function(n,i,a,c){var h=n.memoizedProps;if(h!==c){n=i.stateNode,as(Li.current);var g=null;switch(a){case"input":h=Nt(n,h),c=Nt(n,c),g=[];break;case"select":h=le({},h,{value:void 0}),c=le({},c,{value:void 0}),g=[];break;case"textarea":h=qt(n,h),c=qt(n,c),g=[];break;default:typeof h.onClick!="function"&&typeof c.onClick=="function"&&(n.onclick=$o)}qe(a,c);var T;a=null;for(oe in h)if(!c.hasOwnProperty(oe)&&h.hasOwnProperty(oe)&&h[oe]!=null)if(oe==="style"){var O=h[oe];for(T in O)O.hasOwnProperty(T)&&(a||(a={}),a[T]="")}else oe!=="dangerouslySetInnerHTML"&&oe!=="children"&&oe!=="suppressContentEditableWarning"&&oe!=="suppressHydrationWarning"&&oe!=="autoFocus"&&(o.hasOwnProperty(oe)?g||(g=[]):(g=g||[]).push(oe,null));for(oe in c){var V=c[oe];if(O=h!=null?h[oe]:void 0,c.hasOwnProperty(oe)&&V!==O&&(V!=null||O!=null))if(oe==="style")if(O){for(T in O)!O.hasOwnProperty(T)||V&&V.hasOwnProperty(T)||(a||(a={}),a[T]="");for(T in V)V.hasOwnProperty(T)&&O[T]!==V[T]&&(a||(a={}),a[T]=V[T])}else a||(g||(g=[]),g.push(oe,a)),a=V;else oe==="dangerouslySetInnerHTML"?(V=V?V.__html:void 0,O=O?O.__html:void 0,V!=null&&O!==V&&(g=g||[]).push(oe,V)):oe==="children"?typeof V!="string"&&typeof V!="number"||(g=g||[]).push(oe,""+V):oe!=="suppressContentEditableWarning"&&oe!=="suppressHydrationWarning"&&(o.hasOwnProperty(oe)?(V!=null&&oe==="onScroll"&&Ht("scroll",n),g||O===V||(g=[])):(g=g||[]).push(oe,V))}a&&(g=g||[]).push("style",a);var oe=g;(i.updateQueue=oe)&&(i.flags|=4)}},um=function(n,i,a,c){a!==c&&(i.flags|=4)};function no(n,i){if(!$t)switch(n.tailMode){case"hidden":i=n.tail;for(var a=null;i!==null;)i.alternate!==null&&(a=i),i=i.sibling;a===null?n.tail=null:a.sibling=null;break;case"collapsed":a=n.tail;for(var c=null;a!==null;)a.alternate!==null&&(c=a),a=a.sibling;c===null?i||n.tail===null?n.tail=null:n.tail.sibling=null:c.sibling=null}}function Nn(n){var i=n.alternate!==null&&n.alternate.child===n.child,a=0,c=0;if(i)for(var h=n.child;h!==null;)a|=h.lanes|h.childLanes,c|=h.subtreeFlags&14680064,c|=h.flags&14680064,h.return=n,h=h.sibling;else for(h=n.child;h!==null;)a|=h.lanes|h.childLanes,c|=h.subtreeFlags,c|=h.flags,h.return=n,h=h.sibling;return n.subtreeFlags|=c,n.childLanes=a,i}function dv(n,i,a){var c=i.pendingProps;switch(hu(i),i.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Nn(i),null;case 1:return Wn(i.type)&&Zo(),Nn(i),null;case 3:return c=i.stateNode,Gs(),jt(Gn),jt(An),Tu(),c.pendingContext&&(c.context=c.pendingContext,c.pendingContext=null),(n===null||n.child===null)&&(nl(i)?i.flags|=4:n===null||n.memoizedState.isDehydrated&&(i.flags&256)===0||(i.flags|=1024,_i!==null&&(nd(_i),_i=null))),Wu(n,i),Nn(i),null;case 5:Eu(i);var h=as(Za.current);if(a=i.type,n!==null&&i.stateNode!=null)cm(n,i,a,c,h),n.ref!==i.ref&&(i.flags|=512,i.flags|=2097152);else{if(!c){if(i.stateNode===null)throw Error(t(166));return Nn(i),null}if(n=as(Li.current),nl(i)){c=i.stateNode,a=i.type;var g=i.memoizedProps;switch(c[Pi]=i,c[Xa]=g,n=(i.mode&1)!==0,a){case"dialog":Ht("cancel",c),Ht("close",c);break;case"iframe":case"object":case"embed":Ht("load",c);break;case"video":case"audio":for(h=0;h<ja.length;h++)Ht(ja[h],c);break;case"source":Ht("error",c);break;case"img":case"image":case"link":Ht("error",c),Ht("load",c);break;case"details":Ht("toggle",c);break;case"input":Mt(c,g),Ht("invalid",c);break;case"select":c._wrapperState={wasMultiple:!!g.multiple},Ht("invalid",c);break;case"textarea":W(c,g),Ht("invalid",c)}qe(a,g),h=null;for(var T in g)if(g.hasOwnProperty(T)){var O=g[T];T==="children"?typeof O=="string"?c.textContent!==O&&(g.suppressHydrationWarning!==!0&&Yo(c.textContent,O,n),h=["children",O]):typeof O=="number"&&c.textContent!==""+O&&(g.suppressHydrationWarning!==!0&&Yo(c.textContent,O,n),h=["children",""+O]):o.hasOwnProperty(T)&&O!=null&&T==="onScroll"&&Ht("scroll",c)}switch(a){case"input":et(c),tn(c,g,!0);break;case"textarea":et(c),Tt(c);break;case"select":case"option":break;default:typeof g.onClick=="function"&&(c.onclick=$o)}c=h,i.updateQueue=c,c!==null&&(i.flags|=4)}else{T=h.nodeType===9?h:h.ownerDocument,n==="http://www.w3.org/1999/xhtml"&&(n=F(a)),n==="http://www.w3.org/1999/xhtml"?a==="script"?(n=T.createElement("div"),n.innerHTML="<script><\/script>",n=n.removeChild(n.firstChild)):typeof c.is=="string"?n=T.createElement(a,{is:c.is}):(n=T.createElement(a),a==="select"&&(T=n,c.multiple?T.multiple=!0:c.size&&(T.size=c.size))):n=T.createElementNS(n,a),n[Pi]=i,n[Xa]=c,lm(n,i,!1,!1),i.stateNode=n;e:{switch(T=Le(a,c),a){case"dialog":Ht("cancel",n),Ht("close",n),h=c;break;case"iframe":case"object":case"embed":Ht("load",n),h=c;break;case"video":case"audio":for(h=0;h<ja.length;h++)Ht(ja[h],n);h=c;break;case"source":Ht("error",n),h=c;break;case"img":case"image":case"link":Ht("error",n),Ht("load",n),h=c;break;case"details":Ht("toggle",n),h=c;break;case"input":Mt(n,c),h=Nt(n,c),Ht("invalid",n);break;case"option":h=c;break;case"select":n._wrapperState={wasMultiple:!!c.multiple},h=le({},c,{value:void 0}),Ht("invalid",n);break;case"textarea":W(n,c),h=qt(n,c),Ht("invalid",n);break;default:h=c}qe(a,h),O=h;for(g in O)if(O.hasOwnProperty(g)){var V=O[g];g==="style"?ge(n,V):g==="dangerouslySetInnerHTML"?(V=V?V.__html:void 0,V!=null&&ie(n,V)):g==="children"?typeof V=="string"?(a!=="textarea"||V!=="")&&de(n,V):typeof V=="number"&&de(n,""+V):g!=="suppressContentEditableWarning"&&g!=="suppressHydrationWarning"&&g!=="autoFocus"&&(o.hasOwnProperty(g)?V!=null&&g==="onScroll"&&Ht("scroll",n):V!=null&&U(n,g,V,T))}switch(a){case"input":et(n),tn(n,c,!1);break;case"textarea":et(n),Tt(n);break;case"option":c.value!=null&&n.setAttribute("value",""+me(c.value));break;case"select":n.multiple=!!c.multiple,g=c.value,g!=null?It(n,!!c.multiple,g,!1):c.defaultValue!=null&&It(n,!!c.multiple,c.defaultValue,!0);break;default:typeof h.onClick=="function"&&(n.onclick=$o)}switch(a){case"button":case"input":case"select":case"textarea":c=!!c.autoFocus;break e;case"img":c=!0;break e;default:c=!1}}c&&(i.flags|=4)}i.ref!==null&&(i.flags|=512,i.flags|=2097152)}return Nn(i),null;case 6:if(n&&i.stateNode!=null)um(n,i,n.memoizedProps,c);else{if(typeof c!="string"&&i.stateNode===null)throw Error(t(166));if(a=as(Za.current),as(Li.current),nl(i)){if(c=i.stateNode,a=i.memoizedProps,c[Pi]=i,(g=c.nodeValue!==a)&&(n=Jn,n!==null))switch(n.tag){case 3:Yo(c.nodeValue,a,(n.mode&1)!==0);break;case 5:n.memoizedProps.suppressHydrationWarning!==!0&&Yo(c.nodeValue,a,(n.mode&1)!==0)}g&&(i.flags|=4)}else c=(a.nodeType===9?a:a.ownerDocument).createTextNode(c),c[Pi]=i,i.stateNode=c}return Nn(i),null;case 13:if(jt(Qt),c=i.memoizedState,n===null||n.memoizedState!==null&&n.memoizedState.dehydrated!==null){if($t&&ei!==null&&(i.mode&1)!==0&&(i.flags&128)===0)hp(),Bs(),i.flags|=98560,g=!1;else if(g=nl(i),c!==null&&c.dehydrated!==null){if(n===null){if(!g)throw Error(t(318));if(g=i.memoizedState,g=g!==null?g.dehydrated:null,!g)throw Error(t(317));g[Pi]=i}else Bs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Nn(i),g=!1}else _i!==null&&(nd(_i),_i=null),g=!0;if(!g)return i.flags&65536?i:null}return(i.flags&128)!==0?(i.lanes=a,i):(c=c!==null,c!==(n!==null&&n.memoizedState!==null)&&c&&(i.child.flags|=8192,(i.mode&1)!==0&&(n===null||(Qt.current&1)!==0?dn===0&&(dn=3):sd())),i.updateQueue!==null&&(i.flags|=4),Nn(i),null);case 4:return Gs(),Wu(n,i),n===null&&Ga(i.stateNode.containerInfo),Nn(i),null;case 10:return _u(i.type._context),Nn(i),null;case 17:return Wn(i.type)&&Zo(),Nn(i),null;case 19:if(jt(Qt),g=i.memoizedState,g===null)return Nn(i),null;if(c=(i.flags&128)!==0,T=g.rendering,T===null)if(c)no(g,!1);else{if(dn!==0||n!==null&&(n.flags&128)!==0)for(n=i.child;n!==null;){if(T=ll(n),T!==null){for(i.flags|=128,no(g,!1),c=T.updateQueue,c!==null&&(i.updateQueue=c,i.flags|=4),i.subtreeFlags=0,c=a,a=i.child;a!==null;)g=a,n=c,g.flags&=14680066,T=g.alternate,T===null?(g.childLanes=0,g.lanes=n,g.child=null,g.subtreeFlags=0,g.memoizedProps=null,g.memoizedState=null,g.updateQueue=null,g.dependencies=null,g.stateNode=null):(g.childLanes=T.childLanes,g.lanes=T.lanes,g.child=T.child,g.subtreeFlags=0,g.deletions=null,g.memoizedProps=T.memoizedProps,g.memoizedState=T.memoizedState,g.updateQueue=T.updateQueue,g.type=T.type,n=T.dependencies,g.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext}),a=a.sibling;return zt(Qt,Qt.current&1|2),i.child}n=n.sibling}g.tail!==null&&Zt()>Ys&&(i.flags|=128,c=!0,no(g,!1),i.lanes=4194304)}else{if(!c)if(n=ll(T),n!==null){if(i.flags|=128,c=!0,a=n.updateQueue,a!==null&&(i.updateQueue=a,i.flags|=4),no(g,!0),g.tail===null&&g.tailMode==="hidden"&&!T.alternate&&!$t)return Nn(i),null}else 2*Zt()-g.renderingStartTime>Ys&&a!==1073741824&&(i.flags|=128,c=!0,no(g,!1),i.lanes=4194304);g.isBackwards?(T.sibling=i.child,i.child=T):(a=g.last,a!==null?a.sibling=T:i.child=T,g.last=T)}return g.tail!==null?(i=g.tail,g.rendering=i,g.tail=i.sibling,g.renderingStartTime=Zt(),i.sibling=null,a=Qt.current,zt(Qt,c?a&1|2:a&1),i):(Nn(i),null);case 22:case 23:return rd(),c=i.memoizedState!==null,n!==null&&n.memoizedState!==null!==c&&(i.flags|=8192),c&&(i.mode&1)!==0?(ti&1073741824)!==0&&(Nn(i),i.subtreeFlags&6&&(i.flags|=8192)):Nn(i),null;case 24:return null;case 25:return null}throw Error(t(156,i.tag))}function fv(n,i){switch(hu(i),i.tag){case 1:return Wn(i.type)&&Zo(),n=i.flags,n&65536?(i.flags=n&-65537|128,i):null;case 3:return Gs(),jt(Gn),jt(An),Tu(),n=i.flags,(n&65536)!==0&&(n&128)===0?(i.flags=n&-65537|128,i):null;case 5:return Eu(i),null;case 13:if(jt(Qt),n=i.memoizedState,n!==null&&n.dehydrated!==null){if(i.alternate===null)throw Error(t(340));Bs()}return n=i.flags,n&65536?(i.flags=n&-65537|128,i):null;case 19:return jt(Qt),null;case 4:return Gs(),null;case 10:return _u(i.type._context),null;case 22:case 23:return rd(),null;case 24:return null;default:return null}}var xl=!1,Rn=!1,hv=typeof WeakSet=="function"?WeakSet:Set,Be=null;function Xs(n,i){var a=n.ref;if(a!==null)if(typeof a=="function")try{a(null)}catch(c){rn(n,i,c)}else a.current=null}function Xu(n,i,a){try{a()}catch(c){rn(n,i,c)}}var dm=!1;function pv(n,i){if(ru=ko,n=jh(),Kc(n)){if("selectionStart"in n)var a={start:n.selectionStart,end:n.selectionEnd};else e:{a=(a=n.ownerDocument)&&a.defaultView||window;var c=a.getSelection&&a.getSelection();if(c&&c.rangeCount!==0){a=c.anchorNode;var h=c.anchorOffset,g=c.focusNode;c=c.focusOffset;try{a.nodeType,g.nodeType}catch{a=null;break e}var T=0,O=-1,V=-1,oe=0,Se=0,Me=n,ye=null;t:for(;;){for(var Oe;Me!==a||h!==0&&Me.nodeType!==3||(O=T+h),Me!==g||c!==0&&Me.nodeType!==3||(V=T+c),Me.nodeType===3&&(T+=Me.nodeValue.length),(Oe=Me.firstChild)!==null;)ye=Me,Me=Oe;for(;;){if(Me===n)break t;if(ye===a&&++oe===h&&(O=T),ye===g&&++Se===c&&(V=T),(Oe=Me.nextSibling)!==null)break;Me=ye,ye=Me.parentNode}Me=Oe}a=O===-1||V===-1?null:{start:O,end:V}}else a=null}a=a||{start:0,end:0}}else a=null;for(su={focusedElem:n,selectionRange:a},ko=!1,Be=i;Be!==null;)if(i=Be,n=i.child,(i.subtreeFlags&1028)!==0&&n!==null)n.return=i,Be=n;else for(;Be!==null;){i=Be;try{var je=i.alternate;if((i.flags&1024)!==0)switch(i.tag){case 0:case 11:case 15:break;case 1:if(je!==null){var Xe=je.memoizedProps,an=je.memoizedState,J=i.stateNode,G=J.getSnapshotBeforeUpdate(i.elementType===i.type?Xe:yi(i.type,Xe),an);J.__reactInternalSnapshotBeforeUpdate=G}break;case 3:var ne=i.stateNode.containerInfo;ne.nodeType===1?ne.textContent="":ne.nodeType===9&&ne.documentElement&&ne.removeChild(ne.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(t(163))}}catch(Ee){rn(i,i.return,Ee)}if(n=i.sibling,n!==null){n.return=i.return,Be=n;break}Be=i.return}return je=dm,dm=!1,je}function io(n,i,a){var c=i.updateQueue;if(c=c!==null?c.lastEffect:null,c!==null){var h=c=c.next;do{if((h.tag&n)===n){var g=h.destroy;h.destroy=void 0,g!==void 0&&Xu(i,a,g)}h=h.next}while(h!==c)}}function vl(n,i){if(i=i.updateQueue,i=i!==null?i.lastEffect:null,i!==null){var a=i=i.next;do{if((a.tag&n)===n){var c=a.create;a.destroy=c()}a=a.next}while(a!==i)}}function qu(n){var i=n.ref;if(i!==null){var a=n.stateNode;switch(n.tag){case 5:n=a;break;default:n=a}typeof i=="function"?i(n):i.current=n}}function fm(n){var i=n.alternate;i!==null&&(n.alternate=null,fm(i)),n.child=null,n.deletions=null,n.sibling=null,n.tag===5&&(i=n.stateNode,i!==null&&(delete i[Pi],delete i[Xa],delete i[cu],delete i[K0],delete i[Z0])),n.stateNode=null,n.return=null,n.dependencies=null,n.memoizedProps=null,n.memoizedState=null,n.pendingProps=null,n.stateNode=null,n.updateQueue=null}function hm(n){return n.tag===5||n.tag===3||n.tag===4}function pm(n){e:for(;;){for(;n.sibling===null;){if(n.return===null||hm(n.return))return null;n=n.return}for(n.sibling.return=n.return,n=n.sibling;n.tag!==5&&n.tag!==6&&n.tag!==18;){if(n.flags&2||n.child===null||n.tag===4)continue e;n.child.return=n,n=n.child}if(!(n.flags&2))return n.stateNode}}function Yu(n,i,a){var c=n.tag;if(c===5||c===6)n=n.stateNode,i?a.nodeType===8?a.parentNode.insertBefore(n,i):a.insertBefore(n,i):(a.nodeType===8?(i=a.parentNode,i.insertBefore(n,a)):(i=a,i.appendChild(n)),a=a._reactRootContainer,a!=null||i.onclick!==null||(i.onclick=$o));else if(c!==4&&(n=n.child,n!==null))for(Yu(n,i,a),n=n.sibling;n!==null;)Yu(n,i,a),n=n.sibling}function $u(n,i,a){var c=n.tag;if(c===5||c===6)n=n.stateNode,i?a.insertBefore(n,i):a.appendChild(n);else if(c!==4&&(n=n.child,n!==null))for($u(n,i,a),n=n.sibling;n!==null;)$u(n,i,a),n=n.sibling}var Sn=null,Si=!1;function Cr(n,i,a){for(a=a.child;a!==null;)mm(n,i,a),a=a.sibling}function mm(n,i,a){if(Te&&typeof Te.onCommitFiberUnmount=="function")try{Te.onCommitFiberUnmount(ee,a)}catch{}switch(a.tag){case 5:Rn||Xs(a,i);case 6:var c=Sn,h=Si;Sn=null,Cr(n,i,a),Sn=c,Si=h,Sn!==null&&(Si?(n=Sn,a=a.stateNode,n.nodeType===8?n.parentNode.removeChild(a):n.removeChild(a)):Sn.removeChild(a.stateNode));break;case 18:Sn!==null&&(Si?(n=Sn,a=a.stateNode,n.nodeType===8?lu(n.parentNode,a):n.nodeType===1&&lu(n,a),Ua(n)):lu(Sn,a.stateNode));break;case 4:c=Sn,h=Si,Sn=a.stateNode.containerInfo,Si=!0,Cr(n,i,a),Sn=c,Si=h;break;case 0:case 11:case 14:case 15:if(!Rn&&(c=a.updateQueue,c!==null&&(c=c.lastEffect,c!==null))){h=c=c.next;do{var g=h,T=g.destroy;g=g.tag,T!==void 0&&((g&2)!==0||(g&4)!==0)&&Xu(a,i,T),h=h.next}while(h!==c)}Cr(n,i,a);break;case 1:if(!Rn&&(Xs(a,i),c=a.stateNode,typeof c.componentWillUnmount=="function"))try{c.props=a.memoizedProps,c.state=a.memoizedState,c.componentWillUnmount()}catch(O){rn(a,i,O)}Cr(n,i,a);break;case 21:Cr(n,i,a);break;case 22:a.mode&1?(Rn=(c=Rn)||a.memoizedState!==null,Cr(n,i,a),Rn=c):Cr(n,i,a);break;default:Cr(n,i,a)}}function gm(n){var i=n.updateQueue;if(i!==null){n.updateQueue=null;var a=n.stateNode;a===null&&(a=n.stateNode=new hv),i.forEach(function(c){var h=bv.bind(null,n,c);a.has(c)||(a.add(c),c.then(h,h))})}}function Mi(n,i){var a=i.deletions;if(a!==null)for(var c=0;c<a.length;c++){var h=a[c];try{var g=n,T=i,O=T;e:for(;O!==null;){switch(O.tag){case 5:Sn=O.stateNode,Si=!1;break e;case 3:Sn=O.stateNode.containerInfo,Si=!0;break e;case 4:Sn=O.stateNode.containerInfo,Si=!0;break e}O=O.return}if(Sn===null)throw Error(t(160));mm(g,T,h),Sn=null,Si=!1;var V=h.alternate;V!==null&&(V.return=null),h.return=null}catch(oe){rn(h,i,oe)}}if(i.subtreeFlags&12854)for(i=i.child;i!==null;)xm(i,n),i=i.sibling}function xm(n,i){var a=n.alternate,c=n.flags;switch(n.tag){case 0:case 11:case 14:case 15:if(Mi(i,n),Di(n),c&4){try{io(3,n,n.return),vl(3,n)}catch(Xe){rn(n,n.return,Xe)}try{io(5,n,n.return)}catch(Xe){rn(n,n.return,Xe)}}break;case 1:Mi(i,n),Di(n),c&512&&a!==null&&Xs(a,a.return);break;case 5:if(Mi(i,n),Di(n),c&512&&a!==null&&Xs(a,a.return),n.flags&32){var h=n.stateNode;try{de(h,"")}catch(Xe){rn(n,n.return,Xe)}}if(c&4&&(h=n.stateNode,h!=null)){var g=n.memoizedProps,T=a!==null?a.memoizedProps:g,O=n.type,V=n.updateQueue;if(n.updateQueue=null,V!==null)try{O==="input"&&g.type==="radio"&&g.name!=null&&_t(h,g),Le(O,T);var oe=Le(O,g);for(T=0;T<V.length;T+=2){var Se=V[T],Me=V[T+1];Se==="style"?ge(h,Me):Se==="dangerouslySetInnerHTML"?ie(h,Me):Se==="children"?de(h,Me):U(h,Se,Me,oe)}switch(O){case"input":Xt(h,g);break;case"textarea":_n(h,g);break;case"select":var ye=h._wrapperState.wasMultiple;h._wrapperState.wasMultiple=!!g.multiple;var Oe=g.value;Oe!=null?It(h,!!g.multiple,Oe,!1):ye!==!!g.multiple&&(g.defaultValue!=null?It(h,!!g.multiple,g.defaultValue,!0):It(h,!!g.multiple,g.multiple?[]:"",!1))}h[Xa]=g}catch(Xe){rn(n,n.return,Xe)}}break;case 6:if(Mi(i,n),Di(n),c&4){if(n.stateNode===null)throw Error(t(162));h=n.stateNode,g=n.memoizedProps;try{h.nodeValue=g}catch(Xe){rn(n,n.return,Xe)}}break;case 3:if(Mi(i,n),Di(n),c&4&&a!==null&&a.memoizedState.isDehydrated)try{Ua(i.containerInfo)}catch(Xe){rn(n,n.return,Xe)}break;case 4:Mi(i,n),Di(n);break;case 13:Mi(i,n),Di(n),h=n.child,h.flags&8192&&(g=h.memoizedState!==null,h.stateNode.isHidden=g,!g||h.alternate!==null&&h.alternate.memoizedState!==null||(Qu=Zt())),c&4&&gm(n);break;case 22:if(Se=a!==null&&a.memoizedState!==null,n.mode&1?(Rn=(oe=Rn)||Se,Mi(i,n),Rn=oe):Mi(i,n),Di(n),c&8192){if(oe=n.memoizedState!==null,(n.stateNode.isHidden=oe)&&!Se&&(n.mode&1)!==0)for(Be=n,Se=n.child;Se!==null;){for(Me=Be=Se;Be!==null;){switch(ye=Be,Oe=ye.child,ye.tag){case 0:case 11:case 14:case 15:io(4,ye,ye.return);break;case 1:Xs(ye,ye.return);var je=ye.stateNode;if(typeof je.componentWillUnmount=="function"){c=ye,a=ye.return;try{i=c,je.props=i.memoizedProps,je.state=i.memoizedState,je.componentWillUnmount()}catch(Xe){rn(c,a,Xe)}}break;case 5:Xs(ye,ye.return);break;case 22:if(ye.memoizedState!==null){ym(Me);continue}}Oe!==null?(Oe.return=ye,Be=Oe):ym(Me)}Se=Se.sibling}e:for(Se=null,Me=n;;){if(Me.tag===5){if(Se===null){Se=Me;try{h=Me.stateNode,oe?(g=h.style,typeof g.setProperty=="function"?g.setProperty("display","none","important"):g.display="none"):(O=Me.stateNode,V=Me.memoizedProps.style,T=V!=null&&V.hasOwnProperty("display")?V.display:null,O.style.display=fe("display",T))}catch(Xe){rn(n,n.return,Xe)}}}else if(Me.tag===6){if(Se===null)try{Me.stateNode.nodeValue=oe?"":Me.memoizedProps}catch(Xe){rn(n,n.return,Xe)}}else if((Me.tag!==22&&Me.tag!==23||Me.memoizedState===null||Me===n)&&Me.child!==null){Me.child.return=Me,Me=Me.child;continue}if(Me===n)break e;for(;Me.sibling===null;){if(Me.return===null||Me.return===n)break e;Se===Me&&(Se=null),Me=Me.return}Se===Me&&(Se=null),Me.sibling.return=Me.return,Me=Me.sibling}}break;case 19:Mi(i,n),Di(n),c&4&&gm(n);break;case 21:break;default:Mi(i,n),Di(n)}}function Di(n){var i=n.flags;if(i&2){try{e:{for(var a=n.return;a!==null;){if(hm(a)){var c=a;break e}a=a.return}throw Error(t(160))}switch(c.tag){case 5:var h=c.stateNode;c.flags&32&&(de(h,""),c.flags&=-33);var g=pm(n);$u(n,g,h);break;case 3:case 4:var T=c.stateNode.containerInfo,O=pm(n);Yu(n,O,T);break;default:throw Error(t(161))}}catch(V){rn(n,n.return,V)}n.flags&=-3}i&4096&&(n.flags&=-4097)}function mv(n,i,a){Be=n,vm(n)}function vm(n,i,a){for(var c=(n.mode&1)!==0;Be!==null;){var h=Be,g=h.child;if(h.tag===22&&c){var T=h.memoizedState!==null||xl;if(!T){var O=h.alternate,V=O!==null&&O.memoizedState!==null||Rn;O=xl;var oe=Rn;if(xl=T,(Rn=V)&&!oe)for(Be=h;Be!==null;)T=Be,V=T.child,T.tag===22&&T.memoizedState!==null?Sm(h):V!==null?(V.return=T,Be=V):Sm(h);for(;g!==null;)Be=g,vm(g),g=g.sibling;Be=h,xl=O,Rn=oe}_m(n)}else(h.subtreeFlags&8772)!==0&&g!==null?(g.return=h,Be=g):_m(n)}}function _m(n){for(;Be!==null;){var i=Be;if((i.flags&8772)!==0){var a=i.alternate;try{if((i.flags&8772)!==0)switch(i.tag){case 0:case 11:case 15:Rn||vl(5,i);break;case 1:var c=i.stateNode;if(i.flags&4&&!Rn)if(a===null)c.componentDidMount();else{var h=i.elementType===i.type?a.memoizedProps:yi(i.type,a.memoizedProps);c.componentDidUpdate(h,a.memoizedState,c.__reactInternalSnapshotBeforeUpdate)}var g=i.updateQueue;g!==null&&yp(i,g,c);break;case 3:var T=i.updateQueue;if(T!==null){if(a=null,i.child!==null)switch(i.child.tag){case 5:a=i.child.stateNode;break;case 1:a=i.child.stateNode}yp(i,T,a)}break;case 5:var O=i.stateNode;if(a===null&&i.flags&4){a=O;var V=i.memoizedProps;switch(i.type){case"button":case"input":case"select":case"textarea":V.autoFocus&&a.focus();break;case"img":V.src&&(a.src=V.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(i.memoizedState===null){var oe=i.alternate;if(oe!==null){var Se=oe.memoizedState;if(Se!==null){var Me=Se.dehydrated;Me!==null&&Ua(Me)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;default:throw Error(t(163))}Rn||i.flags&512&&qu(i)}catch(ye){rn(i,i.return,ye)}}if(i===n){Be=null;break}if(a=i.sibling,a!==null){a.return=i.return,Be=a;break}Be=i.return}}function ym(n){for(;Be!==null;){var i=Be;if(i===n){Be=null;break}var a=i.sibling;if(a!==null){a.return=i.return,Be=a;break}Be=i.return}}function Sm(n){for(;Be!==null;){var i=Be;try{switch(i.tag){case 0:case 11:case 15:var a=i.return;try{vl(4,i)}catch(V){rn(i,a,V)}break;case 1:var c=i.stateNode;if(typeof c.componentDidMount=="function"){var h=i.return;try{c.componentDidMount()}catch(V){rn(i,h,V)}}var g=i.return;try{qu(i)}catch(V){rn(i,g,V)}break;case 5:var T=i.return;try{qu(i)}catch(V){rn(i,T,V)}}}catch(V){rn(i,i.return,V)}if(i===n){Be=null;break}var O=i.sibling;if(O!==null){O.return=i.return,Be=O;break}Be=i.return}}var gv=Math.ceil,_l=N.ReactCurrentDispatcher,Ku=N.ReactCurrentOwner,ci=N.ReactCurrentBatchConfig,Et=0,gn=null,ln=null,Mn=0,ti=0,qs=br(0),dn=0,ro=null,ls=0,yl=0,Zu=0,so=null,qn=null,Qu=0,Ys=1/0,Qi=null,Sl=!1,Ju=null,Nr=null,Ml=!1,Rr=null,bl=0,ao=0,ed=null,El=-1,wl=0;function kn(){return(Et&6)!==0?Zt():El!==-1?El:El=Zt()}function Pr(n){return(n.mode&1)===0?1:(Et&2)!==0&&Mn!==0?Mn&-Mn:J0.transition!==null?(wl===0&&(wl=ke()),wl):(n=gt,n!==0||(n=window.event,n=n===void 0?16:bh(n.type)),n)}function bi(n,i,a,c){if(50<ao)throw ao=0,ed=null,Error(t(185));mt(n,a,c),((Et&2)===0||n!==gn)&&(n===gn&&((Et&2)===0&&(yl|=a),dn===4&&Lr(n,Mn)),Yn(n,c),a===1&&Et===0&&(i.mode&1)===0&&(Ys=Zt()+500,Jo&&wr()))}function Yn(n,i){var a=n.callbackNode;Dt(n,i);var c=Ot(n,n===gn?Mn:0);if(c===0)a!==null&&Na(a),n.callbackNode=null,n.callbackPriority=0;else if(i=c&-c,n.callbackPriority!==i){if(a!=null&&Na(a),i===1)n.tag===0?Q0(bm.bind(null,n)):lp(bm.bind(null,n)),Y0(function(){(Et&6)===0&&wr()}),a=null;else{switch(Gi(c)){case 1:a=Ra;break;case 4:a=C;break;case 16:a=X;break;case 536870912:a=te;break;default:a=X}a=Pm(a,Mm.bind(null,n))}n.callbackPriority=i,n.callbackNode=a}}function Mm(n,i){if(El=-1,wl=0,(Et&6)!==0)throw Error(t(327));var a=n.callbackNode;if($s()&&n.callbackNode!==a)return null;var c=Ot(n,n===gn?Mn:0);if(c===0)return null;if((c&30)!==0||(c&n.expiredLanes)!==0||i)i=Tl(n,c);else{i=c;var h=Et;Et|=2;var g=wm();(gn!==n||Mn!==i)&&(Qi=null,Ys=Zt()+500,us(n,i));do try{_v();break}catch(O){Em(n,O)}while(!0);vu(),_l.current=g,Et=h,ln!==null?i=0:(gn=null,Mn=0,i=dn)}if(i!==0){if(i===2&&(h=on(n),h!==0&&(c=h,i=td(n,h))),i===1)throw a=ro,us(n,0),Lr(n,c),Yn(n,Zt()),a;if(i===6)Lr(n,c);else{if(h=n.current.alternate,(c&30)===0&&!xv(h)&&(i=Tl(n,c),i===2&&(g=on(n),g!==0&&(c=g,i=td(n,g))),i===1))throw a=ro,us(n,0),Lr(n,c),Yn(n,Zt()),a;switch(n.finishedWork=h,n.finishedLanes=c,i){case 0:case 1:throw Error(t(345));case 2:ds(n,qn,Qi);break;case 3:if(Lr(n,c),(c&130023424)===c&&(i=Qu+500-Zt(),10<i)){if(Ot(n,0)!==0)break;if(h=n.suspendedLanes,(h&c)!==c){kn(),n.pingedLanes|=n.suspendedLanes&h;break}n.timeoutHandle=ou(ds.bind(null,n,qn,Qi),i);break}ds(n,qn,Qi);break;case 4:if(Lr(n,c),(c&4194240)===c)break;for(i=n.eventTimes,h=-1;0<c;){var T=31-we(c);g=1<<T,T=i[T],T>h&&(h=T),c&=~g}if(c=h,c=Zt()-c,c=(120>c?120:480>c?480:1080>c?1080:1920>c?1920:3e3>c?3e3:4320>c?4320:1960*gv(c/1960))-c,10<c){n.timeoutHandle=ou(ds.bind(null,n,qn,Qi),c);break}ds(n,qn,Qi);break;case 5:ds(n,qn,Qi);break;default:throw Error(t(329))}}}return Yn(n,Zt()),n.callbackNode===a?Mm.bind(null,n):null}function td(n,i){var a=so;return n.current.memoizedState.isDehydrated&&(us(n,i).flags|=256),n=Tl(n,i),n!==2&&(i=qn,qn=a,i!==null&&nd(i)),n}function nd(n){qn===null?qn=n:qn.push.apply(qn,n)}function xv(n){for(var i=n;;){if(i.flags&16384){var a=i.updateQueue;if(a!==null&&(a=a.stores,a!==null))for(var c=0;c<a.length;c++){var h=a[c],g=h.getSnapshot;h=h.value;try{if(!vi(g(),h))return!1}catch{return!1}}}if(a=i.child,i.subtreeFlags&16384&&a!==null)a.return=i,i=a;else{if(i===n)break;for(;i.sibling===null;){if(i.return===null||i.return===n)return!0;i=i.return}i.sibling.return=i.return,i=i.sibling}}return!0}function Lr(n,i){for(i&=~Zu,i&=~yl,n.suspendedLanes|=i,n.pingedLanes&=~i,n=n.expirationTimes;0<i;){var a=31-we(i),c=1<<a;n[a]=-1,i&=~c}}function bm(n){if((Et&6)!==0)throw Error(t(327));$s();var i=Ot(n,0);if((i&1)===0)return Yn(n,Zt()),null;var a=Tl(n,i);if(n.tag!==0&&a===2){var c=on(n);c!==0&&(i=c,a=td(n,c))}if(a===1)throw a=ro,us(n,0),Lr(n,i),Yn(n,Zt()),a;if(a===6)throw Error(t(345));return n.finishedWork=n.current.alternate,n.finishedLanes=i,ds(n,qn,Qi),Yn(n,Zt()),null}function id(n,i){var a=Et;Et|=1;try{return n(i)}finally{Et=a,Et===0&&(Ys=Zt()+500,Jo&&wr())}}function cs(n){Rr!==null&&Rr.tag===0&&(Et&6)===0&&$s();var i=Et;Et|=1;var a=ci.transition,c=gt;try{if(ci.transition=null,gt=1,n)return n()}finally{gt=c,ci.transition=a,Et=i,(Et&6)===0&&wr()}}function rd(){ti=qs.current,jt(qs)}function us(n,i){n.finishedWork=null,n.finishedLanes=0;var a=n.timeoutHandle;if(a!==-1&&(n.timeoutHandle=-1,q0(a)),ln!==null)for(a=ln.return;a!==null;){var c=a;switch(hu(c),c.tag){case 1:c=c.type.childContextTypes,c!=null&&Zo();break;case 3:Gs(),jt(Gn),jt(An),Tu();break;case 5:Eu(c);break;case 4:Gs();break;case 13:jt(Qt);break;case 19:jt(Qt);break;case 10:_u(c.type._context);break;case 22:case 23:rd()}a=a.return}if(gn=n,ln=n=Ir(n.current,null),Mn=ti=i,dn=0,ro=null,Zu=yl=ls=0,qn=so=null,ss!==null){for(i=0;i<ss.length;i++)if(a=ss[i],c=a.interleaved,c!==null){a.interleaved=null;var h=c.next,g=a.pending;if(g!==null){var T=g.next;g.next=h,c.next=T}a.pending=c}ss=null}return n}function Em(n,i){do{var a=ln;try{if(vu(),cl.current=hl,ul){for(var c=Jt.memoizedState;c!==null;){var h=c.queue;h!==null&&(h.pending=null),c=c.next}ul=!1}if(os=0,mn=un=Jt=null,Qa=!1,Ja=0,Ku.current=null,a===null||a.return===null){dn=1,ro=i,ln=null;break}e:{var g=n,T=a.return,O=a,V=i;if(i=Mn,O.flags|=32768,V!==null&&typeof V=="object"&&typeof V.then=="function"){var oe=V,Se=O,Me=Se.tag;if((Se.mode&1)===0&&(Me===0||Me===11||Me===15)){var ye=Se.alternate;ye?(Se.updateQueue=ye.updateQueue,Se.memoizedState=ye.memoizedState,Se.lanes=ye.lanes):(Se.updateQueue=null,Se.memoizedState=null)}var Oe=$p(T);if(Oe!==null){Oe.flags&=-257,Kp(Oe,T,O,g,i),Oe.mode&1&&Yp(g,oe,i),i=Oe,V=oe;var je=i.updateQueue;if(je===null){var Xe=new Set;Xe.add(V),i.updateQueue=Xe}else je.add(V);break e}else{if((i&1)===0){Yp(g,oe,i),sd();break e}V=Error(t(426))}}else if($t&&O.mode&1){var an=$p(T);if(an!==null){(an.flags&65536)===0&&(an.flags|=256),Kp(an,T,O,g,i),gu(Ws(V,O));break e}}g=V=Ws(V,O),dn!==4&&(dn=2),so===null?so=[g]:so.push(g),g=T;do{switch(g.tag){case 3:g.flags|=65536,i&=-i,g.lanes|=i;var J=Xp(g,V,i);_p(g,J);break e;case 1:O=V;var G=g.type,ne=g.stateNode;if((g.flags&128)===0&&(typeof G.getDerivedStateFromError=="function"||ne!==null&&typeof ne.componentDidCatch=="function"&&(Nr===null||!Nr.has(ne)))){g.flags|=65536,i&=-i,g.lanes|=i;var Ee=qp(g,O,i);_p(g,Ee);break e}}g=g.return}while(g!==null)}Am(a)}catch(Ke){i=Ke,ln===a&&a!==null&&(ln=a=a.return);continue}break}while(!0)}function wm(){var n=_l.current;return _l.current=hl,n===null?hl:n}function sd(){(dn===0||dn===3||dn===2)&&(dn=4),gn===null||(ls&268435455)===0&&(yl&268435455)===0||Lr(gn,Mn)}function Tl(n,i){var a=Et;Et|=2;var c=wm();(gn!==n||Mn!==i)&&(Qi=null,us(n,i));do try{vv();break}catch(h){Em(n,h)}while(!0);if(vu(),Et=a,_l.current=c,ln!==null)throw Error(t(261));return gn=null,Mn=0,dn}function vv(){for(;ln!==null;)Tm(ln)}function _v(){for(;ln!==null&&!Uo();)Tm(ln)}function Tm(n){var i=Rm(n.alternate,n,ti);n.memoizedProps=n.pendingProps,i===null?Am(n):ln=i,Ku.current=null}function Am(n){var i=n;do{var a=i.alternate;if(n=i.return,(i.flags&32768)===0){if(a=dv(a,i,ti),a!==null){ln=a;return}}else{if(a=fv(a,i),a!==null){a.flags&=32767,ln=a;return}if(n!==null)n.flags|=32768,n.subtreeFlags=0,n.deletions=null;else{dn=6,ln=null;return}}if(i=i.sibling,i!==null){ln=i;return}ln=i=n}while(i!==null);dn===0&&(dn=5)}function ds(n,i,a){var c=gt,h=ci.transition;try{ci.transition=null,gt=1,yv(n,i,a,c)}finally{ci.transition=h,gt=c}return null}function yv(n,i,a,c){do $s();while(Rr!==null);if((Et&6)!==0)throw Error(t(327));a=n.finishedWork;var h=n.finishedLanes;if(a===null)return null;if(n.finishedWork=null,n.finishedLanes=0,a===n.current)throw Error(t(177));n.callbackNode=null,n.callbackPriority=0;var g=a.lanes|a.childLanes;if(Hn(n,g),n===gn&&(ln=gn=null,Mn=0),(a.subtreeFlags&2064)===0&&(a.flags&2064)===0||Ml||(Ml=!0,Pm(X,function(){return $s(),null})),g=(a.flags&15990)!==0,(a.subtreeFlags&15990)!==0||g){g=ci.transition,ci.transition=null;var T=gt;gt=1;var O=Et;Et|=4,Ku.current=null,pv(n,a),xm(a,n),B0(su),ko=!!ru,su=ru=null,n.current=a,mv(a),kc(),Et=O,gt=T,ci.transition=g}else n.current=a;if(Ml&&(Ml=!1,Rr=n,bl=h),g=n.pendingLanes,g===0&&(Nr=null),ze(a.stateNode),Yn(n,Zt()),i!==null)for(c=n.onRecoverableError,a=0;a<i.length;a++)h=i[a],c(h.value,{componentStack:h.stack,digest:h.digest});if(Sl)throw Sl=!1,n=Ju,Ju=null,n;return(bl&1)!==0&&n.tag!==0&&$s(),g=n.pendingLanes,(g&1)!==0?n===ed?ao++:(ao=0,ed=n):ao=0,wr(),null}function $s(){if(Rr!==null){var n=Gi(bl),i=ci.transition,a=gt;try{if(ci.transition=null,gt=16>n?16:n,Rr===null)var c=!1;else{if(n=Rr,Rr=null,bl=0,(Et&6)!==0)throw Error(t(331));var h=Et;for(Et|=4,Be=n.current;Be!==null;){var g=Be,T=g.child;if((Be.flags&16)!==0){var O=g.deletions;if(O!==null){for(var V=0;V<O.length;V++){var oe=O[V];for(Be=oe;Be!==null;){var Se=Be;switch(Se.tag){case 0:case 11:case 15:io(8,Se,g)}var Me=Se.child;if(Me!==null)Me.return=Se,Be=Me;else for(;Be!==null;){Se=Be;var ye=Se.sibling,Oe=Se.return;if(fm(Se),Se===oe){Be=null;break}if(ye!==null){ye.return=Oe,Be=ye;break}Be=Oe}}}var je=g.alternate;if(je!==null){var Xe=je.child;if(Xe!==null){je.child=null;do{var an=Xe.sibling;Xe.sibling=null,Xe=an}while(Xe!==null)}}Be=g}}if((g.subtreeFlags&2064)!==0&&T!==null)T.return=g,Be=T;else e:for(;Be!==null;){if(g=Be,(g.flags&2048)!==0)switch(g.tag){case 0:case 11:case 15:io(9,g,g.return)}var J=g.sibling;if(J!==null){J.return=g.return,Be=J;break e}Be=g.return}}var G=n.current;for(Be=G;Be!==null;){T=Be;var ne=T.child;if((T.subtreeFlags&2064)!==0&&ne!==null)ne.return=T,Be=ne;else e:for(T=G;Be!==null;){if(O=Be,(O.flags&2048)!==0)try{switch(O.tag){case 0:case 11:case 15:vl(9,O)}}catch(Ke){rn(O,O.return,Ke)}if(O===T){Be=null;break e}var Ee=O.sibling;if(Ee!==null){Ee.return=O.return,Be=Ee;break e}Be=O.return}}if(Et=h,wr(),Te&&typeof Te.onPostCommitFiberRoot=="function")try{Te.onPostCommitFiberRoot(ee,n)}catch{}c=!0}return c}finally{gt=a,ci.transition=i}}return!1}function Cm(n,i,a){i=Ws(a,i),i=Xp(n,i,1),n=Ar(n,i,1),i=kn(),n!==null&&(mt(n,1,i),Yn(n,i))}function rn(n,i,a){if(n.tag===3)Cm(n,n,a);else for(;i!==null;){if(i.tag===3){Cm(i,n,a);break}else if(i.tag===1){var c=i.stateNode;if(typeof i.type.getDerivedStateFromError=="function"||typeof c.componentDidCatch=="function"&&(Nr===null||!Nr.has(c))){n=Ws(a,n),n=qp(i,n,1),i=Ar(i,n,1),n=kn(),i!==null&&(mt(i,1,n),Yn(i,n));break}}i=i.return}}function Sv(n,i,a){var c=n.pingCache;c!==null&&c.delete(i),i=kn(),n.pingedLanes|=n.suspendedLanes&a,gn===n&&(Mn&a)===a&&(dn===4||dn===3&&(Mn&130023424)===Mn&&500>Zt()-Qu?us(n,0):Zu|=a),Yn(n,i)}function Nm(n,i){i===0&&((n.mode&1)===0?i=1:(i=Ye,Ye<<=1,(Ye&130023424)===0&&(Ye=4194304)));var a=kn();n=$i(n,i),n!==null&&(mt(n,i,a),Yn(n,a))}function Mv(n){var i=n.memoizedState,a=0;i!==null&&(a=i.retryLane),Nm(n,a)}function bv(n,i){var a=0;switch(n.tag){case 13:var c=n.stateNode,h=n.memoizedState;h!==null&&(a=h.retryLane);break;case 19:c=n.stateNode;break;default:throw Error(t(314))}c!==null&&c.delete(i),Nm(n,a)}var Rm;Rm=function(n,i,a){if(n!==null)if(n.memoizedProps!==i.pendingProps||Gn.current)Xn=!0;else{if((n.lanes&a)===0&&(i.flags&128)===0)return Xn=!1,uv(n,i,a);Xn=(n.flags&131072)!==0}else Xn=!1,$t&&(i.flags&1048576)!==0&&cp(i,tl,i.index);switch(i.lanes=0,i.tag){case 2:var c=i.type;gl(n,i),n=i.pendingProps;var h=ks(i,An.current);js(i,a),h=Nu(null,i,c,n,h,a);var g=Ru();return i.flags|=1,typeof h=="object"&&h!==null&&typeof h.render=="function"&&h.$$typeof===void 0?(i.tag=1,i.memoizedState=null,i.updateQueue=null,Wn(c)?(g=!0,Qo(i)):g=!1,i.memoizedState=h.state!==null&&h.state!==void 0?h.state:null,Mu(i),h.updater=pl,i.stateNode=h,h._reactInternals=i,Fu(i,c,n,a),i=Bu(null,i,c,!0,g,a)):(i.tag=0,$t&&g&&fu(i),Fn(null,i,h,a),i=i.child),i;case 16:c=i.elementType;e:{switch(gl(n,i),n=i.pendingProps,h=c._init,c=h(c._payload),i.type=c,h=i.tag=wv(c),n=yi(c,n),h){case 0:i=zu(null,i,c,n,a);break e;case 1:i=nm(null,i,c,n,a);break e;case 11:i=Zp(null,i,c,n,a);break e;case 14:i=Qp(null,i,c,yi(c.type,n),a);break e}throw Error(t(306,c,""))}return i;case 0:return c=i.type,h=i.pendingProps,h=i.elementType===c?h:yi(c,h),zu(n,i,c,h,a);case 1:return c=i.type,h=i.pendingProps,h=i.elementType===c?h:yi(c,h),nm(n,i,c,h,a);case 3:e:{if(im(i),n===null)throw Error(t(387));c=i.pendingProps,g=i.memoizedState,h=g.element,vp(n,i),ol(i,c,null,a);var T=i.memoizedState;if(c=T.element,g.isDehydrated)if(g={element:c,isDehydrated:!1,cache:T.cache,pendingSuspenseBoundaries:T.pendingSuspenseBoundaries,transitions:T.transitions},i.updateQueue.baseState=g,i.memoizedState=g,i.flags&256){h=Ws(Error(t(423)),i),i=rm(n,i,c,a,h);break e}else if(c!==h){h=Ws(Error(t(424)),i),i=rm(n,i,c,a,h);break e}else for(ei=Mr(i.stateNode.containerInfo.firstChild),Jn=i,$t=!0,_i=null,a=gp(i,null,c,a),i.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling;else{if(Bs(),c===h){i=Zi(n,i,a);break e}Fn(n,i,c,a)}i=i.child}return i;case 5:return Sp(i),n===null&&mu(i),c=i.type,h=i.pendingProps,g=n!==null?n.memoizedProps:null,T=h.children,au(c,h)?T=null:g!==null&&au(c,g)&&(i.flags|=32),tm(n,i),Fn(n,i,T,a),i.child;case 6:return n===null&&mu(i),null;case 13:return sm(n,i,a);case 4:return bu(i,i.stateNode.containerInfo),c=i.pendingProps,n===null?i.child=Vs(i,null,c,a):Fn(n,i,c,a),i.child;case 11:return c=i.type,h=i.pendingProps,h=i.elementType===c?h:yi(c,h),Zp(n,i,c,h,a);case 7:return Fn(n,i,i.pendingProps,a),i.child;case 8:return Fn(n,i,i.pendingProps.children,a),i.child;case 12:return Fn(n,i,i.pendingProps.children,a),i.child;case 10:e:{if(c=i.type._context,h=i.pendingProps,g=i.memoizedProps,T=h.value,zt(rl,c._currentValue),c._currentValue=T,g!==null)if(vi(g.value,T)){if(g.children===h.children&&!Gn.current){i=Zi(n,i,a);break e}}else for(g=i.child,g!==null&&(g.return=i);g!==null;){var O=g.dependencies;if(O!==null){T=g.child;for(var V=O.firstContext;V!==null;){if(V.context===c){if(g.tag===1){V=Ki(-1,a&-a),V.tag=2;var oe=g.updateQueue;if(oe!==null){oe=oe.shared;var Se=oe.pending;Se===null?V.next=V:(V.next=Se.next,Se.next=V),oe.pending=V}}g.lanes|=a,V=g.alternate,V!==null&&(V.lanes|=a),yu(g.return,a,i),O.lanes|=a;break}V=V.next}}else if(g.tag===10)T=g.type===i.type?null:g.child;else if(g.tag===18){if(T=g.return,T===null)throw Error(t(341));T.lanes|=a,O=T.alternate,O!==null&&(O.lanes|=a),yu(T,a,i),T=g.sibling}else T=g.child;if(T!==null)T.return=g;else for(T=g;T!==null;){if(T===i){T=null;break}if(g=T.sibling,g!==null){g.return=T.return,T=g;break}T=T.return}g=T}Fn(n,i,h.children,a),i=i.child}return i;case 9:return h=i.type,c=i.pendingProps.children,js(i,a),h=oi(h),c=c(h),i.flags|=1,Fn(n,i,c,a),i.child;case 14:return c=i.type,h=yi(c,i.pendingProps),h=yi(c.type,h),Qp(n,i,c,h,a);case 15:return Jp(n,i,i.type,i.pendingProps,a);case 17:return c=i.type,h=i.pendingProps,h=i.elementType===c?h:yi(c,h),gl(n,i),i.tag=1,Wn(c)?(n=!0,Qo(i)):n=!1,js(i,a),Gp(i,c,h),Fu(i,c,h,a),Bu(null,i,c,!0,n,a);case 19:return om(n,i,a);case 22:return em(n,i,a)}throw Error(t(156,i.tag))};function Pm(n,i){return Jr(n,i)}function Ev(n,i,a,c){this.tag=n,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.ref=null,this.pendingProps=i,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=c,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function ui(n,i,a,c){return new Ev(n,i,a,c)}function ad(n){return n=n.prototype,!(!n||!n.isReactComponent)}function wv(n){if(typeof n=="function")return ad(n)?1:0;if(n!=null){if(n=n.$$typeof,n===H)return 11;if(n===Z)return 14}return 2}function Ir(n,i){var a=n.alternate;return a===null?(a=ui(n.tag,i,n.key,n.mode),a.elementType=n.elementType,a.type=n.type,a.stateNode=n.stateNode,a.alternate=n,n.alternate=a):(a.pendingProps=i,a.type=n.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=n.flags&14680064,a.childLanes=n.childLanes,a.lanes=n.lanes,a.child=n.child,a.memoizedProps=n.memoizedProps,a.memoizedState=n.memoizedState,a.updateQueue=n.updateQueue,i=n.dependencies,a.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext},a.sibling=n.sibling,a.index=n.index,a.ref=n.ref,a}function Al(n,i,a,c,h,g){var T=2;if(c=n,typeof n=="function")ad(n)&&(T=1);else if(typeof n=="string")T=5;else e:switch(n){case D:return fs(a.children,h,g,i);case E:T=8,h|=8;break;case I:return n=ui(12,a,i,h|2),n.elementType=I,n.lanes=g,n;case ce:return n=ui(13,a,i,h),n.elementType=ce,n.lanes=g,n;case he:return n=ui(19,a,i,h),n.elementType=he,n.lanes=g,n;case K:return Cl(a,h,g,i);default:if(typeof n=="object"&&n!==null)switch(n.$$typeof){case z:T=10;break e;case B:T=9;break e;case H:T=11;break e;case Z:T=14;break e;case ue:T=16,c=null;break e}throw Error(t(130,n==null?n:typeof n,""))}return i=ui(T,a,i,h),i.elementType=n,i.type=c,i.lanes=g,i}function fs(n,i,a,c){return n=ui(7,n,c,i),n.lanes=a,n}function Cl(n,i,a,c){return n=ui(22,n,c,i),n.elementType=K,n.lanes=a,n.stateNode={isHidden:!1},n}function od(n,i,a){return n=ui(6,n,null,i),n.lanes=a,n}function ld(n,i,a){return i=ui(4,n.children!==null?n.children:[],n.key,i),i.lanes=a,i.stateNode={containerInfo:n.containerInfo,pendingChildren:null,implementation:n.implementation},i}function Tv(n,i,a,c,h){this.tag=i,this.containerInfo=n,this.finishedWork=this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.pendingContext=this.context=null,this.callbackPriority=0,this.eventTimes=yn(0),this.expirationTimes=yn(-1),this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=yn(0),this.identifierPrefix=c,this.onRecoverableError=h,this.mutableSourceEagerHydrationData=null}function cd(n,i,a,c,h,g,T,O,V){return n=new Tv(n,i,a,O,V),i===1?(i=1,g===!0&&(i|=8)):i=0,g=ui(3,null,null,i),n.current=g,g.stateNode=n,g.memoizedState={element:c,isDehydrated:a,cache:null,transitions:null,pendingSuspenseBoundaries:null},Mu(g),n}function Av(n,i,a){var c=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:R,key:c==null?null:""+c,children:n,containerInfo:i,implementation:a}}function Lm(n){if(!n)return Er;n=n._reactInternals;e:{if(Un(n)!==n||n.tag!==1)throw Error(t(170));var i=n;do{switch(i.tag){case 3:i=i.stateNode.context;break e;case 1:if(Wn(i.type)){i=i.stateNode.__reactInternalMemoizedMergedChildContext;break e}}i=i.return}while(i!==null);throw Error(t(171))}if(n.tag===1){var a=n.type;if(Wn(a))return ap(n,a,i)}return i}function Im(n,i,a,c,h,g,T,O,V){return n=cd(a,c,!0,n,h,g,T,O,V),n.context=Lm(null),a=n.current,c=kn(),h=Pr(a),g=Ki(c,h),g.callback=i??null,Ar(a,g,h),n.current.lanes=h,mt(n,h,c),Yn(n,c),n}function Nl(n,i,a,c){var h=i.current,g=kn(),T=Pr(h);return a=Lm(a),i.context===null?i.context=a:i.pendingContext=a,i=Ki(g,T),i.payload={element:n},c=c===void 0?null:c,c!==null&&(i.callback=c),n=Ar(h,i,T),n!==null&&(bi(n,h,T,g),al(n,h,T)),T}function Rl(n){if(n=n.current,!n.child)return null;switch(n.child.tag){case 5:return n.child.stateNode;default:return n.child.stateNode}}function Dm(n,i){if(n=n.memoizedState,n!==null&&n.dehydrated!==null){var a=n.retryLane;n.retryLane=a!==0&&a<i?a:i}}function ud(n,i){Dm(n,i),(n=n.alternate)&&Dm(n,i)}function Cv(){return null}var Um=typeof reportError=="function"?reportError:function(n){console.error(n)};function dd(n){this._internalRoot=n}Pl.prototype.render=dd.prototype.render=function(n){var i=this._internalRoot;if(i===null)throw Error(t(409));Nl(n,i,null,null)},Pl.prototype.unmount=dd.prototype.unmount=function(){var n=this._internalRoot;if(n!==null){this._internalRoot=null;var i=n.containerInfo;cs(function(){Nl(null,n,null,null)}),i[Wi]=null}};function Pl(n){this._internalRoot=n}Pl.prototype.unstable_scheduleHydration=function(n){if(n){var i=Ut();n={blockedOn:null,target:n,priority:i};for(var a=0;a<_r.length&&i!==0&&i<_r[a].priority;a++);_r.splice(a,0,n),a===0&&Sh(n)}};function fd(n){return!(!n||n.nodeType!==1&&n.nodeType!==9&&n.nodeType!==11)}function Ll(n){return!(!n||n.nodeType!==1&&n.nodeType!==9&&n.nodeType!==11&&(n.nodeType!==8||n.nodeValue!==" react-mount-point-unstable "))}function Fm(){}function Nv(n,i,a,c,h){if(h){if(typeof c=="function"){var g=c;c=function(){var oe=Rl(T);g.call(oe)}}var T=Im(i,c,n,0,null,!1,!1,"",Fm);return n._reactRootContainer=T,n[Wi]=T.current,Ga(n.nodeType===8?n.parentNode:n),cs(),T}for(;h=n.lastChild;)n.removeChild(h);if(typeof c=="function"){var O=c;c=function(){var oe=Rl(V);O.call(oe)}}var V=cd(n,0,!1,null,null,!1,!1,"",Fm);return n._reactRootContainer=V,n[Wi]=V.current,Ga(n.nodeType===8?n.parentNode:n),cs(function(){Nl(i,V,a,c)}),V}function Il(n,i,a,c,h){var g=a._reactRootContainer;if(g){var T=g;if(typeof h=="function"){var O=h;h=function(){var V=Rl(T);O.call(V)}}Nl(i,T,n,h)}else T=Nv(a,i,n,h,c);return Rl(T)}Pt=function(n){switch(n.tag){case 3:var i=n.stateNode;if(i.current.memoizedState.isDehydrated){var a=bt(i.pendingLanes);a!==0&&(jn(i,a|1),Yn(i,Zt()),(Et&6)===0&&(Ys=Zt()+500,wr()))}break;case 13:cs(function(){var c=$i(n,1);if(c!==null){var h=kn();bi(c,n,1,h)}}),ud(n,1)}},Vt=function(n){if(n.tag===13){var i=$i(n,134217728);if(i!==null){var a=kn();bi(i,n,134217728,a)}ud(n,134217728)}},gi=function(n){if(n.tag===13){var i=Pr(n),a=$i(n,i);if(a!==null){var c=kn();bi(a,n,i,c)}ud(n,i)}},Ut=function(){return gt},xi=function(n,i){var a=gt;try{return gt=n,i()}finally{gt=a}},tt=function(n,i,a){switch(i){case"input":if(Xt(n,a),i=a.name,a.type==="radio"&&i!=null){for(a=n;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll("input[name="+JSON.stringify(""+i)+'][type="radio"]'),i=0;i<a.length;i++){var c=a[i];if(c!==n&&c.form===n.form){var h=Ko(c);if(!h)throw Error(t(90));Wt(c),Xt(c,h)}}}break;case"textarea":_n(n,a);break;case"select":i=a.value,i!=null&&It(n,!!a.multiple,i,!1)}},Ie=id,ve=cs;var Rv={usingClientEntryPoint:!1,Events:[qa,Us,Ko,pe,Re,id]},oo={findFiberByHostInstance:ts,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"},Pv={bundleType:oo.bundleType,version:oo.version,rendererPackageName:oo.rendererPackageName,rendererConfig:oo.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:N.ReactCurrentDispatcher,findHostInstanceByFiber:function(n){return n=Qr(n),n===null?null:n.stateNode},findFiberByHostInstance:oo.findFiberByHostInstance||Cv,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Dl=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Dl.isDisabled&&Dl.supportsFiber)try{ee=Dl.inject(Pv),Te=Dl}catch{}}return $n.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=Rv,$n.createPortal=function(n,i){var a=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!fd(i))throw Error(t(200));return Av(n,i,null,a)},$n.createRoot=function(n,i){if(!fd(n))throw Error(t(299));var a=!1,c="",h=Um;return i!=null&&(i.unstable_strictMode===!0&&(a=!0),i.identifierPrefix!==void 0&&(c=i.identifierPrefix),i.onRecoverableError!==void 0&&(h=i.onRecoverableError)),i=cd(n,1,!1,null,null,a,!1,c,h),n[Wi]=i.current,Ga(n.nodeType===8?n.parentNode:n),new dd(i)},$n.findDOMNode=function(n){if(n==null)return null;if(n.nodeType===1)return n;var i=n._reactInternals;if(i===void 0)throw typeof n.render=="function"?Error(t(188)):(n=Object.keys(n).join(","),Error(t(268,n)));return n=Qr(i),n=n===null?null:n.stateNode,n},$n.flushSync=function(n){return cs(n)},$n.hydrate=function(n,i,a){if(!Ll(i))throw Error(t(200));return Il(null,n,i,!0,a)},$n.hydrateRoot=function(n,i,a){if(!fd(n))throw Error(t(405));var c=a!=null&&a.hydratedSources||null,h=!1,g="",T=Um;if(a!=null&&(a.unstable_strictMode===!0&&(h=!0),a.identifierPrefix!==void 0&&(g=a.identifierPrefix),a.onRecoverableError!==void 0&&(T=a.onRecoverableError)),i=Im(i,null,n,1,a??null,h,!1,g,T),n[Wi]=i.current,Ga(n),c)for(n=0;n<c.length;n++)a=c[n],h=a._getVersion,h=h(a._source),i.mutableSourceEagerHydrationData==null?i.mutableSourceEagerHydrationData=[a,h]:i.mutableSourceEagerHydrationData.push(a,h);return new Pl(i)},$n.render=function(n,i,a){if(!Ll(i))throw Error(t(200));return Il(null,n,i,!1,a)},$n.unmountComponentAtNode=function(n){if(!Ll(n))throw Error(t(40));return n._reactRootContainer?(cs(function(){Il(null,null,n,!1,function(){n._reactRootContainer=null,n[Wi]=null})}),!0):!1},$n.unstable_batchedUpdates=id,$n.unstable_renderSubtreeIntoContainer=function(n,i,a,c){if(!Ll(a))throw Error(t(200));if(n==null||n._reactInternals===void 0)throw Error(t(38));return Il(n,i,a,!1,c)},$n.version="18.3.1-next-f1338f8080-20240426",$n}var Gm;function Vv(){if(Gm)return md.exports;Gm=1;function s(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(s)}catch(e){console.error(e)}}return s(),md.exports=Bv(),md.exports}var Wm;function Hv(){if(Wm)return Ul;Wm=1;var s=Vv();return Ul.createRoot=s.createRoot,Ul.hydrateRoot=s.hydrateRoot,Ul}var jv=Hv();const Gv=Qg(jv);class vd extends Error{constructor(e,t,r,o){super(r),this.status=e,this.code=t,this.details=o,this.name="ApiError"}}class Wv{constructor(e=""){lo(this,"baseUrl");lo(this,"token",null);lo(this,"merchantId",null);lo(this,"onUnauthorizedCallback",null);this.baseUrl=e}setAuth(e,t){this.merchantId=e,this.token=t}clearAuth(){this.merchantId=null,this.token=null}onUnauthorized(e){this.onUnauthorizedCallback=e}async request(e,t={}){const r=`${this.baseUrl}${e}`,o={"Content-Type":"application/json",Accept:"application/json",...t.headers};this.token&&(o["X-Auth-Token"]=this.token,o.Authorization=`Bearer ${this.token}`),this.merchantId&&(o["X-Merchant-ID"]=this.merchantId);try{const l=await fetch(r,{...t,headers:o});(l.status===401||l.status===403)&&this.onUnauthorizedCallback&&this.onUnauthorizedCallback();const d=await l.json().catch(()=>({}));if(!l.ok){const f=d.detail||l.statusText||"API Error";throw new vd(l.status,d.code||`HTTP_${l.status}`,typeof f=="string"?f:JSON.stringify(f),d.details)}return d}catch(l){throw l instanceof vd?l:new vd(0,"NETWORK_ERROR",l instanceof Error?l.message:"Network request failed")}}async signup(e){return this.request("/api/v1/merchant/auth/signup",{method:"POST",body:JSON.stringify({name:e.name,slug:e.slug,email:e.email,rzp_key_id:e.rzpKeyId||"rzp_test_placeholder",currency:e.currency||"INR",initial_autonomy_level:e.initialAutonomyLevel??1,max_discount_percentage:e.maxDiscountPercentage??15,min_margin_percentage:e.minMarginPercentage??20,max_single_transaction_paise:e.maxSingleTransactionPaise??5e6})})}async login(e){return this.request("/api/v1/merchant/auth/login",{method:"POST",body:JSON.stringify({slug:e.slug,rzp_key_id:e.rzpKeyId,admin_token:e.adminToken})})}async getProfile(){const e=await this.request("/api/v1/merchant/auth/me");return{merchantId:e.merchant_id,name:e.name,slug:e.slug,status:e.status,currency:e.currency,rzpKeyId:e.rzp_key_id,onboardingCompleted:e.onboarding_completed,policies:{autonomyLevel:e.policies.autonomy_level,maxDiscountPercentage:e.policies.max_discount_percentage,minMarginPercentage:e.policies.min_margin_percentage,maxSingleTransactionPaise:e.policies.max_single_transaction_paise,policyHash:e.policies.policy_hash,protocolVersion:e.policies.protocol_version},createdAt:e.created_at}}async completeSetup(e){const t=await this.request("/api/v1/merchant/setup/complete",{method:"POST",body:JSON.stringify({name:e.name,rzp_key_id:e.rzpKeyId,autonomy_level:e.autonomyLevel,max_discount_percentage:e.maxDiscountPercentage,min_margin_percentage:e.minMarginPercentage,max_single_transaction_paise:e.maxSingleTransactionPaise})});return{merchantId:t.merchant_id,name:t.name,slug:t.slug,status:t.status,currency:t.currency,rzpKeyId:t.rzp_key_id,onboardingCompleted:t.onboarding_completed,policies:{autonomyLevel:t.policies.autonomy_level,maxDiscountPercentage:t.policies.max_discount_percentage,minMarginPercentage:t.policies.min_margin_percentage,maxSingleTransactionPaise:t.policies.max_single_transaction_paise,policyHash:t.policies.policy_hash,protocolVersion:t.policies.protocol_version},createdAt:t.created_at}}async getDashboardSummary(){return this.request("/api/v1/merchant/dashboard/summary")}async listProducts(){return this.request("/api/v1/merchant/products")}async createProduct(e){return this.request("/api/v1/merchant/products",{method:"POST",body:JSON.stringify(e)})}async listInventory(){return this.request("/api/v1/merchant/inventory")}async adjustInventory(e){return this.request("/api/v1/merchant/inventory/adjust",{method:"POST",body:JSON.stringify(e)})}async listQuotes(){return this.request("/api/v1/merchant/quotes")}async listOrders(){return this.request("/api/v1/merchant/orders")}async reconcileOrder(e){return this.request(`/api/v1/orders/${e}/reconcile`,{method:"POST"})}async listPayments(){return this.request("/api/v1/merchant/payments")}async listApprovals(e){const t=e?`?status=${e}`:"";return this.request(`/api/v1/merchant/approvals${t}`)}async resolveApproval(e,t){return this.request(`/api/v1/merchant/approvals/${e}/resolve`,{method:"POST",body:JSON.stringify(t)})}async getPolicies(){return this.request("/api/v1/merchant/policies")}async updatePolicies(e){return this.request("/api/v1/merchant/policies",{method:"PUT",body:JSON.stringify(e)})}async getAuditLedger(e=50){return this.request(`/api/v1/merchant/audit?limit=${e}`)}async seedDemoState(){return this.request("/api/v1/merchant/demo/seed",{method:"POST"})}async simulateDemo(e){return this.request("/api/v1/merchant/demo/simulate",{method:"POST",body:JSON.stringify(e)})}async executeGateway(e,t={}){return this.request("/api/v1/gateway/execute",{method:"POST",body:JSON.stringify({capability:e,payload:t})})}}const Bt=new Wv,Jg=xe.createContext(void 0),Fl="arm_auth_token",Ks="arm_merchant_data",kl="arm_auth_expiry",Xv=({children:s})=>{const[e,t]=xe.useState(()=>{try{const A=localStorage.getItem(Ks);return A?JSON.parse(A):null}catch{return null}}),[r,o]=xe.useState(()=>localStorage.getItem(Fl)),[l,d]=xe.useState(!0),[f,p]=xe.useState(!1);xe.useEffect(()=>{if(r&&e){Bt.setAuth(e.merchantId,r);const A=localStorage.getItem(kl);A&&new Date(A).getTime()<Date.now()&&(p(!0),S())}Bt.onUnauthorized(()=>{p(!0),S()}),d(!1)},[]);const m=async A=>{d(!0);try{const v=await Bt.login(A),y={merchantId:v.merchant_id,name:v.name,slug:v.slug,status:v.status,currency:v.currency,rzpKeyId:A.rzpKeyId||"rzp_test_placeholder",onboardingCompleted:v.onboarding_completed,policies:{autonomyLevel:v.policies.autonomy_level,maxDiscountPercentage:v.policies.max_discount_percentage,minMarginPercentage:v.policies.min_margin_percentage,maxSingleTransactionPaise:v.policies.max_single_transaction_paise,policyHash:v.policies.policy_hash,protocolVersion:v.policies.protocol_version}};t(y),o(v.token),p(!1),Bt.setAuth(y.merchantId,v.token),localStorage.setItem(Fl,v.token),localStorage.setItem(Ks,JSON.stringify(y)),localStorage.setItem(kl,v.expires_at)}finally{d(!1)}},_=async A=>{d(!0);try{const v=await Bt.signup(A),y={merchantId:v.merchant_id,name:v.name,slug:v.slug,status:v.status,currency:v.currency,rzpKeyId:A.rzpKeyId||"rzp_test_placeholder",onboardingCompleted:v.onboarding_completed,policies:{autonomyLevel:v.policies.autonomy_level,maxDiscountPercentage:v.policies.max_discount_percentage,minMarginPercentage:v.policies.min_margin_percentage,maxSingleTransactionPaise:v.policies.max_single_transaction_paise,policyHash:v.policies.policy_hash,protocolVersion:v.policies.protocol_version}};t(y),o(v.token),p(!1),Bt.setAuth(y.merchantId,v.token),localStorage.setItem(Fl,v.token),localStorage.setItem(Ks,JSON.stringify(y)),localStorage.setItem(kl,v.expires_at)}finally{d(!1)}},S=()=>{t(null),o(null),Bt.clearAuth(),localStorage.removeItem(Fl),localStorage.removeItem(Ks),localStorage.removeItem(kl)},x=A=>{if(!e)return;const v={...e,...A};t(v),localStorage.setItem(Ks,JSON.stringify(v))},M=async()=>{if(!(!r||!e))try{const A=await Bt.getProfile();t(A),localStorage.setItem(Ks,JSON.stringify(A))}catch{}},w=()=>{p(!1)};return u.jsx(Jg.Provider,{value:{merchant:e,token:r,isAuthenticated:!!e&&!!r,isLoading:l,sessionExpired:f,login:m,signup:_,logout:S,updateProfile:x,refreshProfile:M,dismissExpiredDialog:w},children:s})},pr=()=>{const s=xe.useContext(Jg);if(!s)throw new Error("useAuth must be used within an AuthProvider");return s};function ex(s){var e,t,r="";if(typeof s=="string"||typeof s=="number")r+=s;else if(typeof s=="object")if(Array.isArray(s)){var o=s.length;for(e=0;e<o;e++)s[e]&&(t=ex(s[e]))&&(r&&(r+=" "),r+=t)}else for(t in s)s[t]&&(r&&(r+=" "),r+=t);return r}function qv(){for(var s,e,t=0,r="",o=arguments.length;t<o;t++)(s=arguments[t])&&(e=ex(s))&&(r&&(r+=" "),r+=e);return r}const Zf="-",Yv=s=>{const e=Kv(s),{conflictingClassGroups:t,conflictingClassGroupModifiers:r}=s;return{getClassGroupId:d=>{const f=d.split(Zf);return f[0]===""&&f.length!==1&&f.shift(),tx(f,e)||$v(d)},getConflictingClassGroupIds:(d,f)=>{const p=t[d]||[];return f&&r[d]?[...p,...r[d]]:p}}},tx=(s,e)=>{var d;if(s.length===0)return e.classGroupId;const t=s[0],r=e.nextPart.get(t),o=r?tx(s.slice(1),r):void 0;if(o)return o;if(e.validators.length===0)return;const l=s.join(Zf);return(d=e.validators.find(({validator:f})=>f(l)))==null?void 0:d.classGroupId},Xm=/^\[(.+)\]$/,$v=s=>{if(Xm.test(s)){const e=Xm.exec(s)[1],t=e==null?void 0:e.substring(0,e.indexOf(":"));if(t)return"arbitrary.."+t}},Kv=s=>{const{theme:e,prefix:t}=s,r={nextPart:new Map,validators:[]};return Qv(Object.entries(s.classGroups),t).forEach(([l,d])=>{nf(d,r,l,e)}),r},nf=(s,e,t,r)=>{s.forEach(o=>{if(typeof o=="string"){const l=o===""?e:qm(e,o);l.classGroupId=t;return}if(typeof o=="function"){if(Zv(o)){nf(o(r),e,t,r);return}e.validators.push({validator:o,classGroupId:t});return}Object.entries(o).forEach(([l,d])=>{nf(d,qm(e,l),t,r)})})},qm=(s,e)=>{let t=s;return e.split(Zf).forEach(r=>{t.nextPart.has(r)||t.nextPart.set(r,{nextPart:new Map,validators:[]}),t=t.nextPart.get(r)}),t},Zv=s=>s.isThemeGetter,Qv=(s,e)=>e?s.map(([t,r])=>{const o=r.map(l=>typeof l=="string"?e+l:typeof l=="object"?Object.fromEntries(Object.entries(l).map(([d,f])=>[e+d,f])):l);return[t,o]}):s,Jv=s=>{if(s<1)return{get:()=>{},set:()=>{}};let e=0,t=new Map,r=new Map;const o=(l,d)=>{t.set(l,d),e++,e>s&&(e=0,r=t,t=new Map)};return{get(l){let d=t.get(l);if(d!==void 0)return d;if((d=r.get(l))!==void 0)return o(l,d),d},set(l,d){t.has(l)?t.set(l,d):o(l,d)}}},nx="!",e_=s=>{const{separator:e,experimentalParseClassName:t}=s,r=e.length===1,o=e[0],l=e.length,d=f=>{const p=[];let m=0,_=0,S;for(let v=0;v<f.length;v++){let y=f[v];if(m===0){if(y===o&&(r||f.slice(v,v+l)===e)){p.push(f.slice(_,v)),_=v+l;continue}if(y==="/"){S=v;continue}}y==="["?m++:y==="]"&&m--}const x=p.length===0?f:f.substring(_),M=x.startsWith(nx),w=M?x.substring(1):x,A=S&&S>_?S-_:void 0;return{modifiers:p,hasImportantModifier:M,baseClassName:w,maybePostfixModifierPosition:A}};return t?f=>t({className:f,parseClassName:d}):d},t_=s=>{if(s.length<=1)return s;const e=[];let t=[];return s.forEach(r=>{r[0]==="["?(e.push(...t.sort(),r),t=[]):t.push(r)}),e.push(...t.sort()),e},n_=s=>({cache:Jv(s.cacheSize),parseClassName:e_(s),...Yv(s)}),i_=/\s+/,r_=(s,e)=>{const{parseClassName:t,getClassGroupId:r,getConflictingClassGroupIds:o}=e,l=[],d=s.trim().split(i_);let f="";for(let p=d.length-1;p>=0;p-=1){const m=d[p],{modifiers:_,hasImportantModifier:S,baseClassName:x,maybePostfixModifierPosition:M}=t(m);let w=!!M,A=r(w?x.substring(0,M):x);if(!A){if(!w){f=m+(f.length>0?" "+f:f);continue}if(A=r(x),!A){f=m+(f.length>0?" "+f:f);continue}w=!1}const v=t_(_).join(":"),y=S?v+nx:v,P=y+A;if(l.includes(P))continue;l.push(P);const U=o(A,w);for(let N=0;N<U.length;++N){const L=U[N];l.push(y+L)}f=m+(f.length>0?" "+f:f)}return f};function s_(){let s=0,e,t,r="";for(;s<arguments.length;)(e=arguments[s++])&&(t=ix(e))&&(r&&(r+=" "),r+=t);return r}const ix=s=>{if(typeof s=="string")return s;let e,t="";for(let r=0;r<s.length;r++)s[r]&&(e=ix(s[r]))&&(t&&(t+=" "),t+=e);return t};function a_(s,...e){let t,r,o,l=d;function d(p){const m=e.reduce((_,S)=>S(_),s());return t=n_(m),r=t.cache.get,o=t.cache.set,l=f,f(p)}function f(p){const m=r(p);if(m)return m;const _=r_(p,t);return o(p,_),_}return function(){return l(s_.apply(null,arguments))}}const Gt=s=>{const e=t=>t[s]||[];return e.isThemeGetter=!0,e},rx=/^\[(?:([a-z-]+):)?(.+)\]$/i,o_=/^\d+\/\d+$/,l_=new Set(["px","full","screen"]),c_=/^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/,u_=/\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/,d_=/^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/,f_=/^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/,h_=/^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/,Ji=s=>da(s)||l_.has(s)||o_.test(s),Ur=s=>Ma(s,"length",S_),da=s=>!!s&&!Number.isNaN(Number(s)),_d=s=>Ma(s,"number",da),uo=s=>!!s&&Number.isInteger(Number(s)),p_=s=>s.endsWith("%")&&da(s.slice(0,-1)),ht=s=>rx.test(s),Fr=s=>c_.test(s),m_=new Set(["length","size","percentage"]),g_=s=>Ma(s,m_,sx),x_=s=>Ma(s,"position",sx),v_=new Set(["image","url"]),__=s=>Ma(s,v_,b_),y_=s=>Ma(s,"",M_),fo=()=>!0,Ma=(s,e,t)=>{const r=rx.exec(s);return r?r[1]?typeof e=="string"?r[1]===e:e.has(r[1]):t(r[2]):!1},S_=s=>u_.test(s)&&!d_.test(s),sx=()=>!1,M_=s=>f_.test(s),b_=s=>h_.test(s),E_=()=>{const s=Gt("colors"),e=Gt("spacing"),t=Gt("blur"),r=Gt("brightness"),o=Gt("borderColor"),l=Gt("borderRadius"),d=Gt("borderSpacing"),f=Gt("borderWidth"),p=Gt("contrast"),m=Gt("grayscale"),_=Gt("hueRotate"),S=Gt("invert"),x=Gt("gap"),M=Gt("gradientColorStops"),w=Gt("gradientColorStopPositions"),A=Gt("inset"),v=Gt("margin"),y=Gt("opacity"),P=Gt("padding"),U=Gt("saturate"),N=Gt("scale"),L=Gt("sepia"),R=Gt("skew"),D=Gt("space"),E=Gt("translate"),I=()=>["auto","contain","none"],z=()=>["auto","hidden","clip","visible","scroll"],B=()=>["auto",ht,e],H=()=>[ht,e],ce=()=>["",Ji,Ur],he=()=>["auto",da,ht],Z=()=>["bottom","center","left","left-bottom","left-top","right","right-bottom","right-top","top"],ue=()=>["solid","dashed","dotted","double","none"],K=()=>["normal","multiply","screen","overlay","darken","lighten","color-dodge","color-burn","hard-light","soft-light","difference","exclusion","hue","saturation","color","luminosity"],q=()=>["start","end","center","between","around","evenly","stretch"],se=()=>["","0",ht],le=()=>["auto","avoid","all","avoid-page","page","left","right","column"],k=()=>[da,ht];return{cacheSize:500,separator:":",theme:{colors:[fo],spacing:[Ji,Ur],blur:["none","",Fr,ht],brightness:k(),borderColor:[s],borderRadius:["none","","full",Fr,ht],borderSpacing:H(),borderWidth:ce(),contrast:k(),grayscale:se(),hueRotate:k(),invert:se(),gap:H(),gradientColorStops:[s],gradientColorStopPositions:[p_,Ur],inset:B(),margin:B(),opacity:k(),padding:H(),saturate:k(),scale:k(),sepia:se(),skew:k(),space:H(),translate:H()},classGroups:{aspect:[{aspect:["auto","square","video",ht]}],container:["container"],columns:[{columns:[Fr]}],"break-after":[{"break-after":le()}],"break-before":[{"break-before":le()}],"break-inside":[{"break-inside":["auto","avoid","avoid-page","avoid-column"]}],"box-decoration":[{"box-decoration":["slice","clone"]}],box:[{box:["border","content"]}],display:["block","inline-block","inline","flex","inline-flex","table","inline-table","table-caption","table-cell","table-column","table-column-group","table-footer-group","table-header-group","table-row-group","table-row","flow-root","grid","inline-grid","contents","list-item","hidden"],float:[{float:["right","left","none","start","end"]}],clear:[{clear:["left","right","both","none","start","end"]}],isolation:["isolate","isolation-auto"],"object-fit":[{object:["contain","cover","fill","none","scale-down"]}],"object-position":[{object:[...Z(),ht]}],overflow:[{overflow:z()}],"overflow-x":[{"overflow-x":z()}],"overflow-y":[{"overflow-y":z()}],overscroll:[{overscroll:I()}],"overscroll-x":[{"overscroll-x":I()}],"overscroll-y":[{"overscroll-y":I()}],position:["static","fixed","absolute","relative","sticky"],inset:[{inset:[A]}],"inset-x":[{"inset-x":[A]}],"inset-y":[{"inset-y":[A]}],start:[{start:[A]}],end:[{end:[A]}],top:[{top:[A]}],right:[{right:[A]}],bottom:[{bottom:[A]}],left:[{left:[A]}],visibility:["visible","invisible","collapse"],z:[{z:["auto",uo,ht]}],basis:[{basis:B()}],"flex-direction":[{flex:["row","row-reverse","col","col-reverse"]}],"flex-wrap":[{flex:["wrap","wrap-reverse","nowrap"]}],flex:[{flex:["1","auto","initial","none",ht]}],grow:[{grow:se()}],shrink:[{shrink:se()}],order:[{order:["first","last","none",uo,ht]}],"grid-cols":[{"grid-cols":[fo]}],"col-start-end":[{col:["auto",{span:["full",uo,ht]},ht]}],"col-start":[{"col-start":he()}],"col-end":[{"col-end":he()}],"grid-rows":[{"grid-rows":[fo]}],"row-start-end":[{row:["auto",{span:[uo,ht]},ht]}],"row-start":[{"row-start":he()}],"row-end":[{"row-end":he()}],"grid-flow":[{"grid-flow":["row","col","dense","row-dense","col-dense"]}],"auto-cols":[{"auto-cols":["auto","min","max","fr",ht]}],"auto-rows":[{"auto-rows":["auto","min","max","fr",ht]}],gap:[{gap:[x]}],"gap-x":[{"gap-x":[x]}],"gap-y":[{"gap-y":[x]}],"justify-content":[{justify:["normal",...q()]}],"justify-items":[{"justify-items":["start","end","center","stretch"]}],"justify-self":[{"justify-self":["auto","start","end","center","stretch"]}],"align-content":[{content:["normal",...q(),"baseline"]}],"align-items":[{items:["start","end","center","baseline","stretch"]}],"align-self":[{self:["auto","start","end","center","stretch","baseline"]}],"place-content":[{"place-content":[...q(),"baseline"]}],"place-items":[{"place-items":["start","end","center","baseline","stretch"]}],"place-self":[{"place-self":["auto","start","end","center","stretch"]}],p:[{p:[P]}],px:[{px:[P]}],py:[{py:[P]}],ps:[{ps:[P]}],pe:[{pe:[P]}],pt:[{pt:[P]}],pr:[{pr:[P]}],pb:[{pb:[P]}],pl:[{pl:[P]}],m:[{m:[v]}],mx:[{mx:[v]}],my:[{my:[v]}],ms:[{ms:[v]}],me:[{me:[v]}],mt:[{mt:[v]}],mr:[{mr:[v]}],mb:[{mb:[v]}],ml:[{ml:[v]}],"space-x":[{"space-x":[D]}],"space-x-reverse":["space-x-reverse"],"space-y":[{"space-y":[D]}],"space-y-reverse":["space-y-reverse"],w:[{w:["auto","min","max","fit","svw","lvw","dvw",ht,e]}],"min-w":[{"min-w":[ht,e,"min","max","fit"]}],"max-w":[{"max-w":[ht,e,"none","full","min","max","fit","prose",{screen:[Fr]},Fr]}],h:[{h:[ht,e,"auto","min","max","fit","svh","lvh","dvh"]}],"min-h":[{"min-h":[ht,e,"min","max","fit","svh","lvh","dvh"]}],"max-h":[{"max-h":[ht,e,"min","max","fit","svh","lvh","dvh"]}],size:[{size:[ht,e,"auto","min","max","fit"]}],"font-size":[{text:["base",Fr,Ur]}],"font-smoothing":["antialiased","subpixel-antialiased"],"font-style":["italic","not-italic"],"font-weight":[{font:["thin","extralight","light","normal","medium","semibold","bold","extrabold","black",_d]}],"font-family":[{font:[fo]}],"fvn-normal":["normal-nums"],"fvn-ordinal":["ordinal"],"fvn-slashed-zero":["slashed-zero"],"fvn-figure":["lining-nums","oldstyle-nums"],"fvn-spacing":["proportional-nums","tabular-nums"],"fvn-fraction":["diagonal-fractions","stacked-fractions"],tracking:[{tracking:["tighter","tight","normal","wide","wider","widest",ht]}],"line-clamp":[{"line-clamp":["none",da,_d]}],leading:[{leading:["none","tight","snug","normal","relaxed","loose",Ji,ht]}],"list-image":[{"list-image":["none",ht]}],"list-style-type":[{list:["none","disc","decimal",ht]}],"list-style-position":[{list:["inside","outside"]}],"placeholder-color":[{placeholder:[s]}],"placeholder-opacity":[{"placeholder-opacity":[y]}],"text-alignment":[{text:["left","center","right","justify","start","end"]}],"text-color":[{text:[s]}],"text-opacity":[{"text-opacity":[y]}],"text-decoration":["underline","overline","line-through","no-underline"],"text-decoration-style":[{decoration:[...ue(),"wavy"]}],"text-decoration-thickness":[{decoration:["auto","from-font",Ji,Ur]}],"underline-offset":[{"underline-offset":["auto",Ji,ht]}],"text-decoration-color":[{decoration:[s]}],"text-transform":["uppercase","lowercase","capitalize","normal-case"],"text-overflow":["truncate","text-ellipsis","text-clip"],"text-wrap":[{text:["wrap","nowrap","balance","pretty"]}],indent:[{indent:H()}],"vertical-align":[{align:["baseline","top","middle","bottom","text-top","text-bottom","sub","super",ht]}],whitespace:[{whitespace:["normal","nowrap","pre","pre-line","pre-wrap","break-spaces"]}],break:[{break:["normal","words","all","keep"]}],hyphens:[{hyphens:["none","manual","auto"]}],content:[{content:["none",ht]}],"bg-attachment":[{bg:["fixed","local","scroll"]}],"bg-clip":[{"bg-clip":["border","padding","content","text"]}],"bg-opacity":[{"bg-opacity":[y]}],"bg-origin":[{"bg-origin":["border","padding","content"]}],"bg-position":[{bg:[...Z(),x_]}],"bg-repeat":[{bg:["no-repeat",{repeat:["","x","y","round","space"]}]}],"bg-size":[{bg:["auto","cover","contain",g_]}],"bg-image":[{bg:["none",{"gradient-to":["t","tr","r","br","b","bl","l","tl"]},__]}],"bg-color":[{bg:[s]}],"gradient-from-pos":[{from:[w]}],"gradient-via-pos":[{via:[w]}],"gradient-to-pos":[{to:[w]}],"gradient-from":[{from:[M]}],"gradient-via":[{via:[M]}],"gradient-to":[{to:[M]}],rounded:[{rounded:[l]}],"rounded-s":[{"rounded-s":[l]}],"rounded-e":[{"rounded-e":[l]}],"rounded-t":[{"rounded-t":[l]}],"rounded-r":[{"rounded-r":[l]}],"rounded-b":[{"rounded-b":[l]}],"rounded-l":[{"rounded-l":[l]}],"rounded-ss":[{"rounded-ss":[l]}],"rounded-se":[{"rounded-se":[l]}],"rounded-ee":[{"rounded-ee":[l]}],"rounded-es":[{"rounded-es":[l]}],"rounded-tl":[{"rounded-tl":[l]}],"rounded-tr":[{"rounded-tr":[l]}],"rounded-br":[{"rounded-br":[l]}],"rounded-bl":[{"rounded-bl":[l]}],"border-w":[{border:[f]}],"border-w-x":[{"border-x":[f]}],"border-w-y":[{"border-y":[f]}],"border-w-s":[{"border-s":[f]}],"border-w-e":[{"border-e":[f]}],"border-w-t":[{"border-t":[f]}],"border-w-r":[{"border-r":[f]}],"border-w-b":[{"border-b":[f]}],"border-w-l":[{"border-l":[f]}],"border-opacity":[{"border-opacity":[y]}],"border-style":[{border:[...ue(),"hidden"]}],"divide-x":[{"divide-x":[f]}],"divide-x-reverse":["divide-x-reverse"],"divide-y":[{"divide-y":[f]}],"divide-y-reverse":["divide-y-reverse"],"divide-opacity":[{"divide-opacity":[y]}],"divide-style":[{divide:ue()}],"border-color":[{border:[o]}],"border-color-x":[{"border-x":[o]}],"border-color-y":[{"border-y":[o]}],"border-color-s":[{"border-s":[o]}],"border-color-e":[{"border-e":[o]}],"border-color-t":[{"border-t":[o]}],"border-color-r":[{"border-r":[o]}],"border-color-b":[{"border-b":[o]}],"border-color-l":[{"border-l":[o]}],"divide-color":[{divide:[o]}],"outline-style":[{outline:["",...ue()]}],"outline-offset":[{"outline-offset":[Ji,ht]}],"outline-w":[{outline:[Ji,Ur]}],"outline-color":[{outline:[s]}],"ring-w":[{ring:ce()}],"ring-w-inset":["ring-inset"],"ring-color":[{ring:[s]}],"ring-opacity":[{"ring-opacity":[y]}],"ring-offset-w":[{"ring-offset":[Ji,Ur]}],"ring-offset-color":[{"ring-offset":[s]}],shadow:[{shadow:["","inner","none",Fr,y_]}],"shadow-color":[{shadow:[fo]}],opacity:[{opacity:[y]}],"mix-blend":[{"mix-blend":[...K(),"plus-lighter","plus-darker"]}],"bg-blend":[{"bg-blend":K()}],filter:[{filter:["","none"]}],blur:[{blur:[t]}],brightness:[{brightness:[r]}],contrast:[{contrast:[p]}],"drop-shadow":[{"drop-shadow":["","none",Fr,ht]}],grayscale:[{grayscale:[m]}],"hue-rotate":[{"hue-rotate":[_]}],invert:[{invert:[S]}],saturate:[{saturate:[U]}],sepia:[{sepia:[L]}],"backdrop-filter":[{"backdrop-filter":["","none"]}],"backdrop-blur":[{"backdrop-blur":[t]}],"backdrop-brightness":[{"backdrop-brightness":[r]}],"backdrop-contrast":[{"backdrop-contrast":[p]}],"backdrop-grayscale":[{"backdrop-grayscale":[m]}],"backdrop-hue-rotate":[{"backdrop-hue-rotate":[_]}],"backdrop-invert":[{"backdrop-invert":[S]}],"backdrop-opacity":[{"backdrop-opacity":[y]}],"backdrop-saturate":[{"backdrop-saturate":[U]}],"backdrop-sepia":[{"backdrop-sepia":[L]}],"border-collapse":[{border:["collapse","separate"]}],"border-spacing":[{"border-spacing":[d]}],"border-spacing-x":[{"border-spacing-x":[d]}],"border-spacing-y":[{"border-spacing-y":[d]}],"table-layout":[{table:["auto","fixed"]}],caption:[{caption:["top","bottom"]}],transition:[{transition:["none","all","","colors","opacity","shadow","transform",ht]}],duration:[{duration:k()}],ease:[{ease:["linear","in","out","in-out",ht]}],delay:[{delay:k()}],animate:[{animate:["none","spin","ping","pulse","bounce",ht]}],transform:[{transform:["","gpu","none"]}],scale:[{scale:[N]}],"scale-x":[{"scale-x":[N]}],"scale-y":[{"scale-y":[N]}],rotate:[{rotate:[uo,ht]}],"translate-x":[{"translate-x":[E]}],"translate-y":[{"translate-y":[E]}],"skew-x":[{"skew-x":[R]}],"skew-y":[{"skew-y":[R]}],"transform-origin":[{origin:["center","top","top-right","right","bottom-right","bottom","bottom-left","left","top-left",ht]}],accent:[{accent:["auto",s]}],appearance:[{appearance:["none","auto"]}],cursor:[{cursor:["auto","default","pointer","wait","text","move","help","not-allowed","none","context-menu","progress","cell","crosshair","vertical-text","alias","copy","no-drop","grab","grabbing","all-scroll","col-resize","row-resize","n-resize","e-resize","s-resize","w-resize","ne-resize","nw-resize","se-resize","sw-resize","ew-resize","ns-resize","nesw-resize","nwse-resize","zoom-in","zoom-out",ht]}],"caret-color":[{caret:[s]}],"pointer-events":[{"pointer-events":["none","auto"]}],resize:[{resize:["none","y","x",""]}],"scroll-behavior":[{scroll:["auto","smooth"]}],"scroll-m":[{"scroll-m":H()}],"scroll-mx":[{"scroll-mx":H()}],"scroll-my":[{"scroll-my":H()}],"scroll-ms":[{"scroll-ms":H()}],"scroll-me":[{"scroll-me":H()}],"scroll-mt":[{"scroll-mt":H()}],"scroll-mr":[{"scroll-mr":H()}],"scroll-mb":[{"scroll-mb":H()}],"scroll-ml":[{"scroll-ml":H()}],"scroll-p":[{"scroll-p":H()}],"scroll-px":[{"scroll-px":H()}],"scroll-py":[{"scroll-py":H()}],"scroll-ps":[{"scroll-ps":H()}],"scroll-pe":[{"scroll-pe":H()}],"scroll-pt":[{"scroll-pt":H()}],"scroll-pr":[{"scroll-pr":H()}],"scroll-pb":[{"scroll-pb":H()}],"scroll-pl":[{"scroll-pl":H()}],"snap-align":[{snap:["start","end","center","align-none"]}],"snap-stop":[{snap:["normal","always"]}],"snap-type":[{snap:["none","x","y","both"]}],"snap-strictness":[{snap:["mandatory","proximity"]}],touch:[{touch:["auto","none","manipulation"]}],"touch-x":[{"touch-pan":["x","left","right"]}],"touch-y":[{"touch-pan":["y","up","down"]}],"touch-pz":["touch-pinch-zoom"],select:[{select:["none","text","all","auto"]}],"will-change":[{"will-change":["auto","scroll","contents","transform",ht]}],fill:[{fill:[s,"none"]}],"stroke-w":[{stroke:[Ji,Ur,_d]}],stroke:[{stroke:[s,"none"]}],sr:["sr-only","not-sr-only"],"forced-color-adjust":[{"forced-color-adjust":["auto","none"]}]},conflictingClassGroups:{overflow:["overflow-x","overflow-y"],overscroll:["overscroll-x","overscroll-y"],inset:["inset-x","inset-y","start","end","top","right","bottom","left"],"inset-x":["right","left"],"inset-y":["top","bottom"],flex:["basis","grow","shrink"],gap:["gap-x","gap-y"],p:["px","py","ps","pe","pt","pr","pb","pl"],px:["pr","pl"],py:["pt","pb"],m:["mx","my","ms","me","mt","mr","mb","ml"],mx:["mr","ml"],my:["mt","mb"],size:["w","h"],"font-size":["leading"],"fvn-normal":["fvn-ordinal","fvn-slashed-zero","fvn-figure","fvn-spacing","fvn-fraction"],"fvn-ordinal":["fvn-normal"],"fvn-slashed-zero":["fvn-normal"],"fvn-figure":["fvn-normal"],"fvn-spacing":["fvn-normal"],"fvn-fraction":["fvn-normal"],"line-clamp":["display","overflow"],rounded:["rounded-s","rounded-e","rounded-t","rounded-r","rounded-b","rounded-l","rounded-ss","rounded-se","rounded-ee","rounded-es","rounded-tl","rounded-tr","rounded-br","rounded-bl"],"rounded-s":["rounded-ss","rounded-es"],"rounded-e":["rounded-se","rounded-ee"],"rounded-t":["rounded-tl","rounded-tr"],"rounded-r":["rounded-tr","rounded-br"],"rounded-b":["rounded-br","rounded-bl"],"rounded-l":["rounded-tl","rounded-bl"],"border-spacing":["border-spacing-x","border-spacing-y"],"border-w":["border-w-s","border-w-e","border-w-t","border-w-r","border-w-b","border-w-l"],"border-w-x":["border-w-r","border-w-l"],"border-w-y":["border-w-t","border-w-b"],"border-color":["border-color-s","border-color-e","border-color-t","border-color-r","border-color-b","border-color-l"],"border-color-x":["border-color-r","border-color-l"],"border-color-y":["border-color-t","border-color-b"],"scroll-m":["scroll-mx","scroll-my","scroll-ms","scroll-me","scroll-mt","scroll-mr","scroll-mb","scroll-ml"],"scroll-mx":["scroll-mr","scroll-ml"],"scroll-my":["scroll-mt","scroll-mb"],"scroll-p":["scroll-px","scroll-py","scroll-ps","scroll-pe","scroll-pt","scroll-pr","scroll-pb","scroll-pl"],"scroll-px":["scroll-pr","scroll-pl"],"scroll-py":["scroll-pt","scroll-pb"],touch:["touch-x","touch-y","touch-pz"],"touch-x":["touch"],"touch-y":["touch"],"touch-pz":["touch"]},conflictingClassGroupModifiers:{"font-size":["leading"]}}},w_=a_(E_);function En(...s){return w_(qv(s))}function fn(s){const e=s/100;return new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:2}).format(e)}function ba(s){try{const e=new Date(s),r=new Date().getTime()-e.getTime(),o=Math.floor(r/1e3);if(o<60)return"just now";const l=Math.floor(o/60);if(l<60)return`${l}m ago`;const d=Math.floor(l/60);return d<24?`${d}h ago`:e.toLocaleDateString("en-IN",{month:"short",day:"numeric"})}catch{return s}}/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const T_=s=>s.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),ax=(...s)=>s.filter((e,t,r)=>!!e&&e.trim()!==""&&r.indexOf(e)===t).join(" ").trim();/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var A_={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const C_=xe.forwardRef(({color:s="currentColor",size:e=24,strokeWidth:t=2,absoluteStrokeWidth:r,className:o="",children:l,iconNode:d,...f},p)=>xe.createElement("svg",{ref:p,...A_,width:e,height:e,stroke:s,strokeWidth:r?Number(t)*24/Number(e):t,className:ax("lucide",o),...f},[...d.map(([m,_])=>xe.createElement(m,_)),...Array.isArray(l)?l:[l]]));/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const st=(s,e)=>{const t=xe.forwardRef(({className:r,...o},l)=>xe.createElement(C_,{ref:l,iconNode:e,className:ax(`lucide-${T_(s)}`,r),...o}));return t.displayName=`${s}`,t};/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const N_=[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]],R_=st("Activity",N_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const P_=[["path",{d:"m12 19-7-7 7-7",key:"1l729n"}],["path",{d:"M19 12H5",key:"x3x0zl"}]],Qf=st("ArrowLeft",P_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const L_=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],cr=st("ArrowRight",L_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const I_=[["path",{d:"M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z",key:"3c2336"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]],D_=st("BadgeCheck",I_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const U_=[["path",{d:"M12 8V4H8",key:"hb8ula"}],["rect",{width:"16",height:"12",x:"4",y:"8",rx:"2",key:"enze0r"}],["path",{d:"M2 14h2",key:"vft8re"}],["path",{d:"M20 14h2",key:"4cs60a"}],["path",{d:"M15 13v2",key:"1xurst"}],["path",{d:"M9 13v2",key:"rq6x2g"}]],ox=st("Bot",U_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const F_=[["path",{d:"M2.97 12.92A2 2 0 0 0 2 14.63v3.24a2 2 0 0 0 .97 1.71l3 1.8a2 2 0 0 0 2.06 0L12 19v-5.5l-5-3-4.03 2.42Z",key:"lc1i9w"}],["path",{d:"m7 16.5-4.74-2.85",key:"1o9zyk"}],["path",{d:"m7 16.5 5-3",key:"va8pkn"}],["path",{d:"M7 16.5v5.17",key:"jnp8gn"}],["path",{d:"M12 13.5V19l3.97 2.38a2 2 0 0 0 2.06 0l3-1.8a2 2 0 0 0 .97-1.71v-3.24a2 2 0 0 0-.97-1.71L17 10.5l-5 3Z",key:"8zsnat"}],["path",{d:"m17 16.5-5-3",key:"8arw3v"}],["path",{d:"m17 16.5 4.74-2.85",key:"8rfmw"}],["path",{d:"M17 16.5v5.17",key:"k6z78m"}],["path",{d:"M7.97 4.42A2 2 0 0 0 7 6.13v4.37l5 3 5-3V6.13a2 2 0 0 0-.97-1.71l-3-1.8a2 2 0 0 0-2.06 0l-3 1.8Z",key:"1xygjf"}],["path",{d:"M12 8 7.26 5.15",key:"1vbdud"}],["path",{d:"m12 8 4.74-2.85",key:"3rx089"}],["path",{d:"M12 13.5V8",key:"1io7kd"}]],lx=st("Boxes",F_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const k_=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],O_=st("ChartColumn",k_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const z_=[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]],Jf=st("Check",z_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const B_=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"12",x2:"12",y1:"8",y2:"12",key:"1pkeuh"}],["line",{x1:"12",x2:"12.01",y1:"16",y2:"16",key:"4dfq90"}]],gc=st("CircleAlert",B_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const V_=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]],Wr=st("CircleCheck",V_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const H_=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m15 9-6 6",key:"1uzhvr"}],["path",{d:"m9 9 6 6",key:"z0biqf"}]],j_=st("CircleX",H_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const G_=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["polyline",{points:"12 6 12 12 16 14",key:"68esgv"}]],Rc=st("Clock",G_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const W_=[["rect",{width:"14",height:"14",x:"8",y:"8",rx:"2",ry:"2",key:"17jyea"}],["path",{d:"M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2",key:"zix9uf"}]],X_=st("Copy",W_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const q_=[["rect",{width:"16",height:"16",x:"4",y:"4",rx:"2",key:"14l7u7"}],["rect",{width:"6",height:"6",x:"9",y:"9",rx:"1",key:"5aljv4"}],["path",{d:"M15 2v2",key:"13l42r"}],["path",{d:"M15 20v2",key:"15mkzm"}],["path",{d:"M2 15h2",key:"1gxd5l"}],["path",{d:"M2 9h2",key:"1bbxkp"}],["path",{d:"M20 15h2",key:"19e6y8"}],["path",{d:"M20 9h2",key:"19tzq7"}],["path",{d:"M9 2v2",key:"165o2o"}],["path",{d:"M9 20v2",key:"i2bqo8"}]],Y_=st("Cpu",q_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $_=[["rect",{width:"20",height:"14",x:"2",y:"5",rx:"2",key:"ynyp8z"}],["line",{x1:"2",x2:"22",y1:"10",y2:"10",key:"1b3vmo"}]],eh=st("CreditCard",$_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const K_=[["ellipse",{cx:"12",cy:"5",rx:"9",ry:"3",key:"msslwz"}],["path",{d:"M3 5V19A9 3 0 0 0 21 19V5",key:"1wlel7"}],["path",{d:"M3 12A9 3 0 0 0 21 12",key:"mv7ke4"}]],Z_=st("Database",K_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Q_=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],yd=st("ExternalLink",Q_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const J_=[["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",key:"1rqfz7"}],["path",{d:"M14 2v4a2 2 0 0 0 2 2h4",key:"tnqrlb"}],["path",{d:"m9 15 2 2 4-4",key:"1grp1n"}]],ey=st("FileCheck",J_);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ty=[["path",{d:"M12 17h.01",key:"p32p05"}],["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z",key:"1mlx9k"}],["path",{d:"M9.1 9a3 3 0 0 1 5.82 1c0 2-3 3-3 3",key:"mhlwft"}]],ny=st("FileQuestion",ty);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const iy=[["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",key:"1rqfz7"}],["path",{d:"M14 2v4a2 2 0 0 0 2 2h4",key:"tnqrlb"}],["path",{d:"M8 13h2",key:"yr2amv"}],["path",{d:"M14 13h2",key:"un5t4a"}],["path",{d:"M8 17h2",key:"2yhykz"}],["path",{d:"M14 17h2",key:"10kma7"}]],ry=st("FileSpreadsheet",iy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const sy=[["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",key:"1rqfz7"}],["path",{d:"M14 2v4a2 2 0 0 0 2 2h4",key:"tnqrlb"}],["path",{d:"M10 9H8",key:"b1mrlr"}],["path",{d:"M16 13H8",key:"t4e002"}],["path",{d:"M16 17H8",key:"z1uh3a"}]],th=st("FileText",sy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ay=[["line",{x1:"4",x2:"20",y1:"9",y2:"9",key:"4lhtct"}],["line",{x1:"4",x2:"20",y1:"15",y2:"15",key:"vyu0kd"}],["line",{x1:"10",x2:"8",y1:"3",y2:"21",key:"1ggp8o"}],["line",{x1:"16",x2:"14",y1:"3",y2:"21",key:"weycgp"}]],oy=st("Hash",ay);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ly=[["path",{d:"M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z",key:"1s6t7t"}],["circle",{cx:"16.5",cy:"7.5",r:".5",fill:"currentColor",key:"w0ekpg"}]],cy=st("KeyRound",ly);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const uy=[["path",{d:"M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z",key:"zw3jo"}],["path",{d:"M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12",key:"1wduqc"}],["path",{d:"M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17",key:"kqbvx6"}]],cx=st("Layers",uy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const dy=[["rect",{width:"7",height:"9",x:"3",y:"3",rx:"1",key:"10lvy0"}],["rect",{width:"7",height:"5",x:"14",y:"3",rx:"1",key:"16une8"}],["rect",{width:"7",height:"9",x:"14",y:"12",rx:"1",key:"1hutg5"}],["rect",{width:"7",height:"5",x:"3",y:"16",rx:"1",key:"ldoo1y"}]],ux=st("LayoutDashboard",dy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fy=[["path",{d:"M21 12a9 9 0 1 1-6.219-8.56",key:"13zald"}]],hy=st("LoaderCircle",fy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const py=[["rect",{width:"18",height:"11",x:"3",y:"11",rx:"2",ry:"2",key:"1w4ew1"}],["path",{d:"M7 11V7a5 5 0 0 1 10 0v4",key:"fwvmzm"}]],xc=st("Lock",py);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const my=[["path",{d:"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",key:"1uf3rs"}],["polyline",{points:"16 17 21 12 16 7",key:"1gabdz"}],["line",{x1:"21",x2:"9",y1:"12",y2:"12",key:"1uyos4"}]],Ym=st("LogOut",my);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gy=[["line",{x1:"4",x2:"20",y1:"12",y2:"12",key:"1e0a9i"}],["line",{x1:"4",x2:"20",y1:"6",y2:"6",key:"1owob3"}],["line",{x1:"4",x2:"20",y1:"18",y2:"18",key:"yk5zj1"}]],xy=st("Menu",gy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vy=[["path",{d:"m5 19-2 2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2",key:"1xuzuj"}],["path",{d:"M9 10h6",key:"9gxzsh"}],["path",{d:"M12 7v6",key:"lw1j43"}],["path",{d:"M9 17h6",key:"r8uit2"}]],_y=st("MessageSquareDiff",vy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yy=[["rect",{x:"16",y:"16",width:"6",height:"6",rx:"1",key:"4q2zg0"}],["rect",{x:"2",y:"16",width:"6",height:"6",rx:"1",key:"8cvhb9"}],["rect",{x:"9",y:"2",width:"6",height:"6",rx:"1",key:"1egb70"}],["path",{d:"M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3",key:"1jsf9p"}],["path",{d:"M12 12V8",key:"2874zd"}]],Sy=st("Network",yy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const My=[["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}],["circle",{cx:"19",cy:"5",r:"2",key:"mhkx31"}],["circle",{cx:"5",cy:"19",r:"2",key:"v8kfzx"}],["path",{d:"M10.4 21.9a10 10 0 0 0 9.941-15.416",key:"eohfx2"}],["path",{d:"M13.5 2.1a10 10 0 0 0-9.841 15.416",key:"19pvbm"}]],by=st("Orbit",My);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ey=[["path",{d:"M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z",key:"1a0edw"}],["path",{d:"M12 22V12",key:"d0xqtd"}],["polyline",{points:"3.29 7 12 12 20.71 7",key:"ousv84"}],["path",{d:"m7.5 4.27 9 5.15",key:"1c824w"}]],vc=st("Package",Ey);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wy=[["path",{d:"M12 20h9",key:"t2du7b"}],["path",{d:"M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z",key:"1ykcvy"}]],Ty=st("PenLine",wy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ay=[["polygon",{points:"6 3 20 12 6 21 6 3",key:"1oa8hb"}]],Cy=st("Play",Ay);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ny=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]],Ry=st("Plus",Ny);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Py=[["path",{d:"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8",key:"v9h5vc"}],["path",{d:"M21 3v5h-5",key:"1q7to0"}],["path",{d:"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16",key:"3uifl3"}],["path",{d:"M8 16H3v5",key:"1cv678"}]],Ly=st("RefreshCw",Py);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Iy=[["path",{d:"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8",key:"1357e3"}],["path",{d:"M3 3v5h5",key:"1xhq8a"}]],Dy=st("RotateCcw",Iy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Uy=[["path",{d:"m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z",key:"7g6ntu"}],["path",{d:"m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z",key:"ijws7r"}],["path",{d:"M7 21h10",key:"1b0cd5"}],["path",{d:"M12 3v18",key:"108xh3"}],["path",{d:"M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2",key:"3gwbw2"}]],dx=st("Scale",Uy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Fy=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M12 16h.01",key:"1drbdi"}]],fx=st("ShieldAlert",Fy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ky=[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]],Pc=st("ShieldCheck",ky);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Oy=[["circle",{cx:"8",cy:"21",r:"1",key:"jimo8o"}],["circle",{cx:"19",cy:"21",r:"1",key:"13723u"}],["path",{d:"M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12",key:"9zh506"}]],hx=st("ShoppingCart",Oy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zy=[["line",{x1:"4",x2:"4",y1:"21",y2:"14",key:"1p332r"}],["line",{x1:"4",x2:"4",y1:"10",y2:"3",key:"gb41h5"}],["line",{x1:"12",x2:"12",y1:"21",y2:"12",key:"hf2csr"}],["line",{x1:"12",x2:"12",y1:"8",y2:"3",key:"1kfi7u"}],["line",{x1:"20",x2:"20",y1:"21",y2:"16",key:"1lhrwl"}],["line",{x1:"20",x2:"20",y1:"12",y2:"3",key:"16vvfq"}],["line",{x1:"2",x2:"6",y1:"14",y2:"14",key:"1uebub"}],["line",{x1:"10",x2:"14",y1:"8",y2:"8",key:"1yglbp"}],["line",{x1:"18",x2:"22",y1:"16",y2:"16",key:"1jxqpz"}]],px=st("SlidersVertical",zy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const By=[["path",{d:"M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z",key:"4pj2yx"}],["path",{d:"M20 3v4",key:"1olli1"}],["path",{d:"M22 5h-4",key:"1gvqau"}],["path",{d:"M4 17v2",key:"vumght"}],["path",{d:"M5 18H3",key:"zchphs"}]],rf=st("Sparkles",By);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Vy=[["polyline",{points:"4 17 10 11 4 5",key:"akl6gq"}],["line",{x1:"12",x2:"20",y1:"19",y2:"19",key:"q2wloq"}]],Hy=st("Terminal",Vy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jy=[["polyline",{points:"22 7 13.5 15.5 8.5 10.5 2 17",key:"126l90"}],["polyline",{points:"16 7 22 7 22 13",key:"kwv8wd"}]],Gy=st("TrendingUp",jy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Wy=[["path",{d:"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",key:"wmoenq"}],["path",{d:"M12 9v4",key:"juzpu7"}],["path",{d:"M12 17h.01",key:"p32p05"}]],ma=st("TriangleAlert",Wy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xy=[["path",{d:"M18 16.98h-5.99c-1.1 0-1.95.94-2.48 1.9A4 4 0 0 1 2 17c.01-.7.2-1.4.57-2",key:"q3hayz"}],["path",{d:"m6 17 3.13-5.78c.53-.97.1-2.18-.5-3.1a4 4 0 1 1 6.89-4.06",key:"1go1hn"}],["path",{d:"m12 6 3.13 5.73C15.66 12.7 16.9 13 18 13a4 4 0 0 1 0 8",key:"qlwsc0"}]],qy=st("Webhook",Xy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Yy=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],mx=st("X",Yy);/**
 * @license lucide-react v0.475.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $y=[["path",{d:"M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",key:"1xq2db"}]],Ky=st("Zap",$y),dt=Nc.forwardRef(({className:s,variant:e="primary",size:t="md",isLoading:r=!1,children:o,disabled:l,...d},f)=>{const p="inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 select-none",m={primary:"bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm active:scale-[0.98]",secondary:"bg-secondary text-secondary-foreground hover:bg-secondary/80",outline:"border border-border bg-transparent hover:bg-accent hover:text-accent-foreground",ghost:"hover:bg-accent hover:text-accent-foreground",destructive:"bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm",link:"text-primary underline-offset-4 hover:underline p-0 h-auto"},_={sm:"h-8 rounded-md px-3 text-xs gap-1.5",md:"h-10 rounded-md px-4 py-2 text-sm gap-2",lg:"h-12 rounded-md px-6 text-base gap-2.5",icon:"h-10 w-10 rounded-md p-0"};return u.jsxs("button",{ref:f,className:En(p,m[e],_[t],s),disabled:l||r,...d,children:[r&&u.jsx(hy,{className:"h-4 w-4 animate-spin text-current"}),o]})});dt.displayName="Button";/**
 * @license
 * Copyright 2010-2026 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const nh="185",Zy=0,$m=1,Qy=2,uc=1,Jy=2,So=3,Xr=0,Zn=1,sr=2,or=0,fa=1,Km=2,Zm=3,Qm=4,eS=5,vs=100,tS=101,nS=102,iS=103,rS=104,sS=200,aS=201,oS=202,lS=203,sf=204,af=205,cS=206,uS=207,dS=208,fS=209,hS=210,pS=211,mS=212,gS=213,xS=214,of=0,lf=1,cf=2,ga=3,uf=4,df=5,ff=6,hf=7,gx=0,vS=1,_S=2,Bi=0,xx=1,vx=2,_x=3,yx=4,Sx=5,Mx=6,bx=7,Ex=300,Ms=301,xa=302,Sd=303,Md=304,Lc=306,pf=1e3,ar=1001,mf=1002,wn=1003,yS=1004,Ol=1005,In=1006,bd=1007,ys=1008,pi=1009,wx=1010,Tx=1011,wo=1012,ih=1013,Hi=1014,Oi=1015,ur=1016,rh=1017,sh=1018,To=1020,Ax=35902,Cx=35899,Nx=1021,Rx=1022,Ci=1023,dr=1026,Ss=1027,Px=1028,ah=1029,bs=1030,oh=1031,lh=1033,dc=33776,fc=33777,hc=33778,pc=33779,gf=35840,xf=35841,vf=35842,_f=35843,yf=36196,Sf=37492,Mf=37496,bf=37488,Ef=37489,_c=37490,wf=37491,Tf=37808,Af=37809,Cf=37810,Nf=37811,Rf=37812,Pf=37813,Lf=37814,If=37815,Df=37816,Uf=37817,Ff=37818,kf=37819,Of=37820,zf=37821,Bf=36492,Vf=36494,Hf=36495,jf=36283,Gf=36284,yc=36285,Wf=36286,SS=3200,Jm=0,MS=1,jr="",fi="srgb",Sc="srgb-linear",Mc="linear",Ft="srgb",Zs=7680,eg=519,bS=512,ES=513,wS=514,ch=515,TS=516,AS=517,uh=518,CS=519,tg=35044,ng="300 es",zi=2e3,bc=2001;function NS(s){for(let e=s.length-1;e>=0;--e)if(s[e]>=65535)return!0;return!1}function Ec(s){return document.createElementNS("http://www.w3.org/1999/xhtml",s)}function RS(){const s=Ec("canvas");return s.style.display="block",s}const ig={};function rg(...s){const e="THREE."+s.shift();console.log(e,...s)}function Lx(s){const e=s[0];if(typeof e=="string"&&e.startsWith("TSL:")){const t=s[1];t&&t.isStackTrace?s[0]+=" "+t.getLocation():s[1]='Stack trace not available. Enable "THREE.Node.captureStackTrace" to capture stack traces.'}return s}function rt(...s){s=Lx(s);const e="THREE."+s.shift();{const t=s[0];t&&t.isStackTrace?console.warn(t.getError(e)):console.warn(e,...s)}}function wt(...s){s=Lx(s);const e="THREE."+s.shift();{const t=s[0];t&&t.isStackTrace?console.error(t.getError(e)):console.error(e,...s)}}function ha(...s){const e=s.join(" ");e in ig||(ig[e]=!0,rt(...s))}function PS(s,e,t){return new Promise(function(r,o){function l(){switch(s.clientWaitSync(e,s.SYNC_FLUSH_COMMANDS_BIT,0)){case s.WAIT_FAILED:o();break;case s.TIMEOUT_EXPIRED:setTimeout(l,t);break;default:r()}}setTimeout(l,t)})}const LS={[of]:lf,[cf]:ff,[uf]:hf,[ga]:df,[lf]:of,[ff]:cf,[hf]:uf,[df]:ga};class ws{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const r=this._listeners;r[e]===void 0&&(r[e]=[]),r[e].indexOf(t)===-1&&r[e].push(t)}hasEventListener(e,t){const r=this._listeners;return r===void 0?!1:r[e]!==void 0&&r[e].indexOf(t)!==-1}removeEventListener(e,t){const r=this._listeners;if(r===void 0)return;const o=r[e];if(o!==void 0){const l=o.indexOf(t);l!==-1&&o.splice(l,1)}}dispatchEvent(e){const t=this._listeners;if(t===void 0)return;const r=t[e.type];if(r!==void 0){e.target=this;const o=r.slice(0);for(let l=0,d=o.length;l<d;l++)o[l].call(this,e);e.target=null}}}const Pn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],Ed=Math.PI/180,Xf=180/Math.PI;function Ao(){const s=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,r=Math.random()*4294967295|0;return(Pn[s&255]+Pn[s>>8&255]+Pn[s>>16&255]+Pn[s>>24&255]+"-"+Pn[e&255]+Pn[e>>8&255]+"-"+Pn[e>>16&15|64]+Pn[e>>24&255]+"-"+Pn[t&63|128]+Pn[t>>8&255]+"-"+Pn[t>>16&255]+Pn[t>>24&255]+Pn[r&255]+Pn[r>>8&255]+Pn[r>>16&255]+Pn[r>>24&255]).toLowerCase()}function vt(s,e,t){return Math.max(e,Math.min(t,s))}function IS(s,e){return(s%e+e)%e}function wd(s,e,t){return(1-t)*s+t*e}function ho(s,e){switch(e.constructor){case Float32Array:return s;case Uint32Array:return s/4294967295;case Uint16Array:return s/65535;case Uint8Array:return s/255;case Int32Array:return Math.max(s/2147483647,-1);case Int16Array:return Math.max(s/32767,-1);case Int8Array:return Math.max(s/127,-1);default:throw new Error("THREE.MathUtils: Invalid component type.")}}function Kn(s,e){switch(e.constructor){case Float32Array:return s;case Uint32Array:return Math.round(s*4294967295);case Uint16Array:return Math.round(s*65535);case Uint8Array:return Math.round(s*255);case Int32Array:return Math.round(s*2147483647);case Int16Array:return Math.round(s*32767);case Int8Array:return Math.round(s*127);default:throw new Error("THREE.MathUtils: Invalid component type.")}}const mh=class mh{constructor(e=0,t=0){this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("THREE.Vector2: index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("THREE.Vector2: index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,r=this.y,o=e.elements;return this.x=o[0]*t+o[3]*r+o[6],this.y=o[1]*t+o[4]*r+o[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=vt(this.x,e.x,t.x),this.y=vt(this.y,e.y,t.y),this}clampScalar(e,t){return this.x=vt(this.x,e,t),this.y=vt(this.y,e,t),this}clampLength(e,t){const r=this.length();return this.divideScalar(r||1).multiplyScalar(vt(r,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const r=this.dot(e)/t;return Math.acos(vt(r,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,r=this.y-e.y;return t*t+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,r){return this.x=e.x+(t.x-e.x)*r,this.y=e.y+(t.y-e.y)*r,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const r=Math.cos(t),o=Math.sin(t),l=this.x-e.x,d=this.y-e.y;return this.x=l*r-d*o+e.x,this.y=l*o+d*r+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}};mh.prototype.isVector2=!0;let yt=mh;class Ea{constructor(e=0,t=0,r=0,o=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=r,this._w=o}static slerpFlat(e,t,r,o,l,d,f){let p=r[o+0],m=r[o+1],_=r[o+2],S=r[o+3],x=l[d+0],M=l[d+1],w=l[d+2],A=l[d+3];if(S!==A||p!==x||m!==M||_!==w){let v=p*x+m*M+_*w+S*A;v<0&&(x=-x,M=-M,w=-w,A=-A,v=-v);let y=1-f;if(v<.9995){const P=Math.acos(v),U=Math.sin(P);y=Math.sin(y*P)/U,f=Math.sin(f*P)/U,p=p*y+x*f,m=m*y+M*f,_=_*y+w*f,S=S*y+A*f}else{p=p*y+x*f,m=m*y+M*f,_=_*y+w*f,S=S*y+A*f;const P=1/Math.sqrt(p*p+m*m+_*_+S*S);p*=P,m*=P,_*=P,S*=P}}e[t]=p,e[t+1]=m,e[t+2]=_,e[t+3]=S}static multiplyQuaternionsFlat(e,t,r,o,l,d){const f=r[o],p=r[o+1],m=r[o+2],_=r[o+3],S=l[d],x=l[d+1],M=l[d+2],w=l[d+3];return e[t]=f*w+_*S+p*M-m*x,e[t+1]=p*w+_*x+m*S-f*M,e[t+2]=m*w+_*M+f*x-p*S,e[t+3]=_*w-f*S-p*x-m*M,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,r,o){return this._x=e,this._y=t,this._z=r,this._w=o,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const r=e._x,o=e._y,l=e._z,d=e._order,f=Math.cos,p=Math.sin,m=f(r/2),_=f(o/2),S=f(l/2),x=p(r/2),M=p(o/2),w=p(l/2);switch(d){case"XYZ":this._x=x*_*S+m*M*w,this._y=m*M*S-x*_*w,this._z=m*_*w+x*M*S,this._w=m*_*S-x*M*w;break;case"YXZ":this._x=x*_*S+m*M*w,this._y=m*M*S-x*_*w,this._z=m*_*w-x*M*S,this._w=m*_*S+x*M*w;break;case"ZXY":this._x=x*_*S-m*M*w,this._y=m*M*S+x*_*w,this._z=m*_*w+x*M*S,this._w=m*_*S-x*M*w;break;case"ZYX":this._x=x*_*S-m*M*w,this._y=m*M*S+x*_*w,this._z=m*_*w-x*M*S,this._w=m*_*S+x*M*w;break;case"YZX":this._x=x*_*S+m*M*w,this._y=m*M*S+x*_*w,this._z=m*_*w-x*M*S,this._w=m*_*S-x*M*w;break;case"XZY":this._x=x*_*S-m*M*w,this._y=m*M*S-x*_*w,this._z=m*_*w+x*M*S,this._w=m*_*S+x*M*w;break;default:rt("Quaternion: .setFromEuler() encountered an unknown order: "+d)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const r=t/2,o=Math.sin(r);return this._x=e.x*o,this._y=e.y*o,this._z=e.z*o,this._w=Math.cos(r),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,r=t[0],o=t[4],l=t[8],d=t[1],f=t[5],p=t[9],m=t[2],_=t[6],S=t[10],x=r+f+S;if(x>0){const M=.5/Math.sqrt(x+1);this._w=.25/M,this._x=(_-p)*M,this._y=(l-m)*M,this._z=(d-o)*M}else if(r>f&&r>S){const M=2*Math.sqrt(1+r-f-S);this._w=(_-p)/M,this._x=.25*M,this._y=(o+d)/M,this._z=(l+m)/M}else if(f>S){const M=2*Math.sqrt(1+f-r-S);this._w=(l-m)/M,this._x=(o+d)/M,this._y=.25*M,this._z=(p+_)/M}else{const M=2*Math.sqrt(1+S-r-f);this._w=(d-o)/M,this._x=(l+m)/M,this._y=(p+_)/M,this._z=.25*M}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let r=e.dot(t)+1;return r<1e-8?(r=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=r):(this._x=0,this._y=-e.z,this._z=e.y,this._w=r)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=r),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(vt(this.dot(e),-1,1)))}rotateTowards(e,t){const r=this.angleTo(e);if(r===0)return this;const o=Math.min(1,t/r);return this.slerp(e,o),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const r=e._x,o=e._y,l=e._z,d=e._w,f=t._x,p=t._y,m=t._z,_=t._w;return this._x=r*_+d*f+o*m-l*p,this._y=o*_+d*p+l*f-r*m,this._z=l*_+d*m+r*p-o*f,this._w=d*_-r*f-o*p-l*m,this._onChangeCallback(),this}slerp(e,t){let r=e._x,o=e._y,l=e._z,d=e._w,f=this.dot(e);f<0&&(r=-r,o=-o,l=-l,d=-d,f=-f);let p=1-t;if(f<.9995){const m=Math.acos(f),_=Math.sin(m);p=Math.sin(p*m)/_,t=Math.sin(t*m)/_,this._x=this._x*p+r*t,this._y=this._y*p+o*t,this._z=this._z*p+l*t,this._w=this._w*p+d*t,this._onChangeCallback()}else this._x=this._x*p+r*t,this._y=this._y*p+o*t,this._z=this._z*p+l*t,this._w=this._w*p+d*t,this.normalize();return this}slerpQuaternions(e,t,r){return this.copy(e).slerp(t,r)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),r=Math.random(),o=Math.sqrt(1-r),l=Math.sqrt(r);return this.set(o*Math.sin(e),o*Math.cos(e),l*Math.sin(t),l*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}const gh=class gh{constructor(e=0,t=0,r=0){this.x=e,this.y=t,this.z=r}set(e,t,r){return r===void 0&&(r=this.z),this.x=e,this.y=t,this.z=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("THREE.Vector3: index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("THREE.Vector3: index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(sg.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(sg.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,r=this.y,o=this.z,l=e.elements;return this.x=l[0]*t+l[3]*r+l[6]*o,this.y=l[1]*t+l[4]*r+l[7]*o,this.z=l[2]*t+l[5]*r+l[8]*o,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,r=this.y,o=this.z,l=e.elements,d=1/(l[3]*t+l[7]*r+l[11]*o+l[15]);return this.x=(l[0]*t+l[4]*r+l[8]*o+l[12])*d,this.y=(l[1]*t+l[5]*r+l[9]*o+l[13])*d,this.z=(l[2]*t+l[6]*r+l[10]*o+l[14])*d,this}applyQuaternion(e){const t=this.x,r=this.y,o=this.z,l=e.x,d=e.y,f=e.z,p=e.w,m=2*(d*o-f*r),_=2*(f*t-l*o),S=2*(l*r-d*t);return this.x=t+p*m+d*S-f*_,this.y=r+p*_+f*m-l*S,this.z=o+p*S+l*_-d*m,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,r=this.y,o=this.z,l=e.elements;return this.x=l[0]*t+l[4]*r+l[8]*o,this.y=l[1]*t+l[5]*r+l[9]*o,this.z=l[2]*t+l[6]*r+l[10]*o,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=vt(this.x,e.x,t.x),this.y=vt(this.y,e.y,t.y),this.z=vt(this.z,e.z,t.z),this}clampScalar(e,t){return this.x=vt(this.x,e,t),this.y=vt(this.y,e,t),this.z=vt(this.z,e,t),this}clampLength(e,t){const r=this.length();return this.divideScalar(r||1).multiplyScalar(vt(r,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,r){return this.x=e.x+(t.x-e.x)*r,this.y=e.y+(t.y-e.y)*r,this.z=e.z+(t.z-e.z)*r,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const r=e.x,o=e.y,l=e.z,d=t.x,f=t.y,p=t.z;return this.x=o*p-l*f,this.y=l*d-r*p,this.z=r*f-o*d,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const r=e.dot(this)/t;return this.copy(e).multiplyScalar(r)}projectOnPlane(e){return Td.copy(this).projectOnVector(e),this.sub(Td)}reflect(e){return this.sub(Td.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const r=this.dot(e)/t;return Math.acos(vt(r,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,r=this.y-e.y,o=this.z-e.z;return t*t+r*r+o*o}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,r){const o=Math.sin(t)*e;return this.x=o*Math.sin(r),this.y=Math.cos(t)*e,this.z=o*Math.cos(r),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,r){return this.x=e*Math.sin(t),this.y=r,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),r=this.setFromMatrixColumn(e,1).length(),o=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=r,this.z=o,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,r=Math.sqrt(1-t*t);return this.x=r*Math.cos(e),this.y=t,this.z=r*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}};gh.prototype.isVector3=!0;let Y=gh;const Td=new Y,sg=new Ea,xh=class xh{constructor(e,t,r,o,l,d,f,p,m){this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,r,o,l,d,f,p,m)}set(e,t,r,o,l,d,f,p,m){const _=this.elements;return _[0]=e,_[1]=o,_[2]=f,_[3]=t,_[4]=l,_[5]=p,_[6]=r,_[7]=d,_[8]=m,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,r=e.elements;return t[0]=r[0],t[1]=r[1],t[2]=r[2],t[3]=r[3],t[4]=r[4],t[5]=r[5],t[6]=r[6],t[7]=r[7],t[8]=r[8],this}extractBasis(e,t,r){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),r.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const r=e.elements,o=t.elements,l=this.elements,d=r[0],f=r[3],p=r[6],m=r[1],_=r[4],S=r[7],x=r[2],M=r[5],w=r[8],A=o[0],v=o[3],y=o[6],P=o[1],U=o[4],N=o[7],L=o[2],R=o[5],D=o[8];return l[0]=d*A+f*P+p*L,l[3]=d*v+f*U+p*R,l[6]=d*y+f*N+p*D,l[1]=m*A+_*P+S*L,l[4]=m*v+_*U+S*R,l[7]=m*y+_*N+S*D,l[2]=x*A+M*P+w*L,l[5]=x*v+M*U+w*R,l[8]=x*y+M*N+w*D,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],r=e[1],o=e[2],l=e[3],d=e[4],f=e[5],p=e[6],m=e[7],_=e[8];return t*d*_-t*f*m-r*l*_+r*f*p+o*l*m-o*d*p}invert(){const e=this.elements,t=e[0],r=e[1],o=e[2],l=e[3],d=e[4],f=e[5],p=e[6],m=e[7],_=e[8],S=_*d-f*m,x=f*p-_*l,M=m*l-d*p,w=t*S+r*x+o*M;if(w===0)return this.set(0,0,0,0,0,0,0,0,0);const A=1/w;return e[0]=S*A,e[1]=(o*m-_*r)*A,e[2]=(f*r-o*d)*A,e[3]=x*A,e[4]=(_*t-o*p)*A,e[5]=(o*l-f*t)*A,e[6]=M*A,e[7]=(r*p-m*t)*A,e[8]=(d*t-r*l)*A,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,r,o,l,d,f){const p=Math.cos(l),m=Math.sin(l);return this.set(r*p,r*m,-r*(p*d+m*f)+d+e,-o*m,o*p,-o*(-m*d+p*f)+f+t,0,0,1),this}scale(e,t){return ha("Matrix3: .scale() is deprecated. Use .makeScale() instead."),this.premultiply(Ad.makeScale(e,t)),this}rotate(e){return ha("Matrix3: .rotate() is deprecated. Use .makeRotation() instead."),this.premultiply(Ad.makeRotation(-e)),this}translate(e,t){return ha("Matrix3: .translate() is deprecated. Use .makeTranslation() instead."),this.premultiply(Ad.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),r=Math.sin(e);return this.set(t,-r,0,r,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,r=e.elements;for(let o=0;o<9;o++)if(t[o]!==r[o])return!1;return!0}fromArray(e,t=0){for(let r=0;r<9;r++)this.elements[r]=e[r+t];return this}toArray(e=[],t=0){const r=this.elements;return e[t]=r[0],e[t+1]=r[1],e[t+2]=r[2],e[t+3]=r[3],e[t+4]=r[4],e[t+5]=r[5],e[t+6]=r[6],e[t+7]=r[7],e[t+8]=r[8],e}clone(){return new this.constructor().fromArray(this.elements)}};xh.prototype.isMatrix3=!0;let ut=xh;const Ad=new ut,ag=new ut().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),og=new ut().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function DS(){const s={enabled:!0,workingColorSpace:Sc,spaces:{},convert:function(o,l,d){return this.enabled===!1||l===d||!l||!d||(this.spaces[l].transfer===Ft&&(o.r=lr(o.r),o.g=lr(o.g),o.b=lr(o.b)),this.spaces[l].primaries!==this.spaces[d].primaries&&(o.applyMatrix3(this.spaces[l].toXYZ),o.applyMatrix3(this.spaces[d].fromXYZ)),this.spaces[d].transfer===Ft&&(o.r=pa(o.r),o.g=pa(o.g),o.b=pa(o.b))),o},workingToColorSpace:function(o,l){return this.convert(o,this.workingColorSpace,l)},colorSpaceToWorking:function(o,l){return this.convert(o,l,this.workingColorSpace)},getPrimaries:function(o){return this.spaces[o].primaries},getTransfer:function(o){return o===jr?Mc:this.spaces[o].transfer},getToneMappingMode:function(o){return this.spaces[o].outputColorSpaceConfig.toneMappingMode||"standard"},getLuminanceCoefficients:function(o,l=this.workingColorSpace){return o.fromArray(this.spaces[l].luminanceCoefficients)},define:function(o){Object.assign(this.spaces,o)},_getMatrix:function(o,l,d){return o.copy(this.spaces[l].toXYZ).multiply(this.spaces[d].fromXYZ)},_getDrawingBufferColorSpace:function(o){return this.spaces[o].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(o=this.workingColorSpace){return this.spaces[o].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(o,l){return ha("ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace()."),s.workingToColorSpace(o,l)},toWorkingColorSpace:function(o,l){return ha("ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking()."),s.colorSpaceToWorking(o,l)}},e=[.64,.33,.3,.6,.15,.06],t=[.2126,.7152,.0722],r=[.3127,.329];return s.define({[Sc]:{primaries:e,whitePoint:r,transfer:Mc,toXYZ:ag,fromXYZ:og,luminanceCoefficients:t,workingColorSpaceConfig:{unpackColorSpace:fi},outputColorSpaceConfig:{drawingBufferColorSpace:fi}},[fi]:{primaries:e,whitePoint:r,transfer:Ft,toXYZ:ag,fromXYZ:og,luminanceCoefficients:t,outputColorSpaceConfig:{drawingBufferColorSpace:fi}}}),s}const St=DS();function lr(s){return s<.04045?s*.0773993808:Math.pow(s*.9478672986+.0521327014,2.4)}function pa(s){return s<.0031308?s*12.92:1.055*Math.pow(s,.41666)-.055}let Qs;class US{static getDataURL(e,t="image/png"){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let r;if(e instanceof HTMLCanvasElement)r=e;else{Qs===void 0&&(Qs=Ec("canvas")),Qs.width=e.width,Qs.height=e.height;const o=Qs.getContext("2d");e instanceof ImageData?o.putImageData(e,0,0):o.drawImage(e,0,0,e.width,e.height),r=Qs}return r.toDataURL(t)}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Ec("canvas");t.width=e.width,t.height=e.height;const r=t.getContext("2d");r.drawImage(e,0,0,e.width,e.height);const o=r.getImageData(0,0,e.width,e.height),l=o.data;for(let d=0;d<l.length;d++)l[d]=lr(l[d]/255)*255;return r.putImageData(o,0,0),t}else if(e.data){const t=e.data.slice(0);for(let r=0;r<t.length;r++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[r]=Math.floor(lr(t[r]/255)*255):t[r]=lr(t[r]);return{data:t,width:e.width,height:e.height}}else return rt("ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let FS=0;class dh{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:FS++}),this.uuid=Ao(),this.data=e,this.dataReady=!0,this.version=0}getSize(e){const t=this.data;return typeof HTMLVideoElement<"u"&&t instanceof HTMLVideoElement?e.set(t.videoWidth,t.videoHeight,0):typeof VideoFrame<"u"&&t instanceof VideoFrame?e.set(t.displayWidth,t.displayHeight,0):t!==null?e.set(t.width,t.height,t.depth||0):e.set(0,0,0),e}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const r={uuid:this.uuid,url:""},o=this.data;if(o!==null){let l;if(Array.isArray(o)){l=[];for(let d=0,f=o.length;d<f;d++)o[d].isDataTexture?l.push(Cd(o[d].image)):l.push(Cd(o[d]))}else l=Cd(o);r.url=l}return t||(e.images[this.uuid]=r),r}}function Cd(s){return typeof HTMLImageElement<"u"&&s instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&s instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&s instanceof ImageBitmap?US.getDataURL(s):s.data?{data:Array.from(s.data),width:s.width,height:s.height,type:s.data.constructor.name}:(rt("Texture: Unable to serialize Texture."),{})}let kS=0;const Nd=new Y;class zn extends ws{constructor(e=zn.DEFAULT_IMAGE,t=zn.DEFAULT_MAPPING,r=ar,o=ar,l=In,d=ys,f=Ci,p=pi,m=zn.DEFAULT_ANISOTROPY,_=jr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:kS++}),this.uuid=Ao(),this.name="",this.source=new dh(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=r,this.wrapT=o,this.magFilter=l,this.minFilter=d,this.anisotropy=m,this.format=f,this.internalFormat=null,this.type=p,this.offset=new yt(0,0),this.repeat=new yt(1,1),this.center=new yt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ut,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=_,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(e&&e.depth&&e.depth>1),this.pmremVersion=0,this.normalized=!1}get width(){return this.source.getSize(Nd).x}get height(){return this.source.getSize(Nd).y}get depth(){return this.source.getSize(Nd).z}get image(){return this.source.data}set image(e){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.normalized=e.normalized,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.renderTarget=e.renderTarget,this.isRenderTargetTexture=e.isRenderTargetTexture,this.isArrayTexture=e.isArrayTexture,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}setValues(e){for(const t in e){const r=e[t];if(r===void 0){rt(`Texture.setValues(): parameter '${t}' has value of undefined.`);continue}const o=this[t];if(o===void 0){rt(`Texture.setValues(): property '${t}' does not exist.`);continue}o&&r&&o.isVector2&&r.isVector2||o&&r&&o.isVector3&&r.isVector3||o&&r&&o.isMatrix3&&r.isMatrix3?o.copy(r):this[t]=r}}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const r={metadata:{version:4.7,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,normalized:this.normalized,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(r.userData=this.userData),t||(e.textures[this.uuid]=r),r}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Ex)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case pf:e.x=e.x-Math.floor(e.x);break;case ar:e.x=e.x<0?0:1;break;case mf:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case pf:e.y=e.y-Math.floor(e.y);break;case ar:e.y=e.y<0?0:1;break;case mf:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}zn.DEFAULT_IMAGE=null;zn.DEFAULT_MAPPING=Ex;zn.DEFAULT_ANISOTROPY=1;const vh=class vh{constructor(e=0,t=0,r=0,o=1){this.x=e,this.y=t,this.z=r,this.w=o}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,r,o){return this.x=e,this.y=t,this.z=r,this.w=o,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("THREE.Vector4: index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("THREE.Vector4: index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,r=this.y,o=this.z,l=this.w,d=e.elements;return this.x=d[0]*t+d[4]*r+d[8]*o+d[12]*l,this.y=d[1]*t+d[5]*r+d[9]*o+d[13]*l,this.z=d[2]*t+d[6]*r+d[10]*o+d[14]*l,this.w=d[3]*t+d[7]*r+d[11]*o+d[15]*l,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,r,o,l;const p=e.elements,m=p[0],_=p[4],S=p[8],x=p[1],M=p[5],w=p[9],A=p[2],v=p[6],y=p[10];if(Math.abs(_-x)<.01&&Math.abs(S-A)<.01&&Math.abs(w-v)<.01){if(Math.abs(_+x)<.1&&Math.abs(S+A)<.1&&Math.abs(w+v)<.1&&Math.abs(m+M+y-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const U=(m+1)/2,N=(M+1)/2,L=(y+1)/2,R=(_+x)/4,D=(S+A)/4,E=(w+v)/4;return U>N&&U>L?U<.01?(r=0,o=.707106781,l=.707106781):(r=Math.sqrt(U),o=R/r,l=D/r):N>L?N<.01?(r=.707106781,o=0,l=.707106781):(o=Math.sqrt(N),r=R/o,l=E/o):L<.01?(r=.707106781,o=.707106781,l=0):(l=Math.sqrt(L),r=D/l,o=E/l),this.set(r,o,l,t),this}let P=Math.sqrt((v-w)*(v-w)+(S-A)*(S-A)+(x-_)*(x-_));return Math.abs(P)<.001&&(P=1),this.x=(v-w)/P,this.y=(S-A)/P,this.z=(x-_)/P,this.w=Math.acos((m+M+y-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=vt(this.x,e.x,t.x),this.y=vt(this.y,e.y,t.y),this.z=vt(this.z,e.z,t.z),this.w=vt(this.w,e.w,t.w),this}clampScalar(e,t){return this.x=vt(this.x,e,t),this.y=vt(this.y,e,t),this.z=vt(this.z,e,t),this.w=vt(this.w,e,t),this}clampLength(e,t){const r=this.length();return this.divideScalar(r||1).multiplyScalar(vt(r,e,t))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,r){return this.x=e.x+(t.x-e.x)*r,this.y=e.y+(t.y-e.y)*r,this.z=e.z+(t.z-e.z)*r,this.w=e.w+(t.w-e.w)*r,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}};vh.prototype.isVector4=!0;let sn=vh;class OS extends ws{constructor(e=1,t=1,r={}){super(),r=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:In,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1,useArrayDepthTexture:!1},r),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=r.depth,this.scissor=new sn(0,0,e,t),this.scissorTest=!1,this.viewport=new sn(0,0,e,t),this.textures=[];const o={width:e,height:t,depth:r.depth},l=new zn(o),d=r.count;for(let f=0;f<d;f++)this.textures[f]=l.clone(),this.textures[f].isRenderTargetTexture=!0,this.textures[f].renderTarget=this;this._setTextureOptions(r),this.depthBuffer=r.depthBuffer,this.stencilBuffer=r.stencilBuffer,this.resolveDepthBuffer=r.resolveDepthBuffer,this.resolveStencilBuffer=r.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=r.depthTexture,this.samples=r.samples,this.multiview=r.multiview,this.useArrayDepthTexture=r.useArrayDepthTexture}_setTextureOptions(e={}){const t={minFilter:In,generateMipmaps:!1,flipY:!1,internalFormat:null};e.mapping!==void 0&&(t.mapping=e.mapping),e.wrapS!==void 0&&(t.wrapS=e.wrapS),e.wrapT!==void 0&&(t.wrapT=e.wrapT),e.wrapR!==void 0&&(t.wrapR=e.wrapR),e.magFilter!==void 0&&(t.magFilter=e.magFilter),e.minFilter!==void 0&&(t.minFilter=e.minFilter),e.format!==void 0&&(t.format=e.format),e.type!==void 0&&(t.type=e.type),e.anisotropy!==void 0&&(t.anisotropy=e.anisotropy),e.colorSpace!==void 0&&(t.colorSpace=e.colorSpace),e.flipY!==void 0&&(t.flipY=e.flipY),e.generateMipmaps!==void 0&&(t.generateMipmaps=e.generateMipmaps),e.internalFormat!==void 0&&(t.internalFormat=e.internalFormat);for(let r=0;r<this.textures.length;r++)this.textures[r].setValues(t)}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}set depthTexture(e){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),e!==null&&(e.renderTarget=this),this._depthTexture=e}get depthTexture(){return this._depthTexture}setSize(e,t,r=1){if(this.width!==e||this.height!==t||this.depth!==r){this.width=e,this.height=t,this.depth=r;for(let o=0,l=this.textures.length;o<l;o++)this.textures[o].image.width=e,this.textures[o].image.height=t,this.textures[o].image.depth=r,this.textures[o].isData3DTexture!==!0&&(this.textures[o].isArrayTexture=this.textures[o].image.depth>1);this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let t=0,r=e.textures.length;t<r;t++){this.textures[t]=e.textures[t].clone(),this.textures[t].isRenderTargetTexture=!0,this.textures[t].renderTarget=this;const o=Object.assign({},e.textures[t].image);this.textures[t].source=new dh(o)}return this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this.multiview=e.multiview,this.useArrayDepthTexture=e.useArrayDepthTexture,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Vi extends OS{constructor(e=1,t=1,r={}){super(e,t,r),this.isWebGLRenderTarget=!0}}class Ix extends zn{constructor(e=null,t=1,r=1,o=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:r,depth:o},this.magFilter=wn,this.minFilter=wn,this.wrapR=ar,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class zS extends zn{constructor(e=null,t=1,r=1,o=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:r,depth:o},this.magFilter=wn,this.minFilter=wn,this.wrapR=ar,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Cc=class Cc{constructor(e,t,r,o,l,d,f,p,m,_,S,x,M,w,A,v){this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,r,o,l,d,f,p,m,_,S,x,M,w,A,v)}set(e,t,r,o,l,d,f,p,m,_,S,x,M,w,A,v){const y=this.elements;return y[0]=e,y[4]=t,y[8]=r,y[12]=o,y[1]=l,y[5]=d,y[9]=f,y[13]=p,y[2]=m,y[6]=_,y[10]=S,y[14]=x,y[3]=M,y[7]=w,y[11]=A,y[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Cc().fromArray(this.elements)}copy(e){const t=this.elements,r=e.elements;return t[0]=r[0],t[1]=r[1],t[2]=r[2],t[3]=r[3],t[4]=r[4],t[5]=r[5],t[6]=r[6],t[7]=r[7],t[8]=r[8],t[9]=r[9],t[10]=r[10],t[11]=r[11],t[12]=r[12],t[13]=r[13],t[14]=r[14],t[15]=r[15],this}copyPosition(e){const t=this.elements,r=e.elements;return t[12]=r[12],t[13]=r[13],t[14]=r[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,r){return this.determinantAffine()===0?(e.set(1,0,0),t.set(0,1,0),r.set(0,0,1),this):(e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),r.setFromMatrixColumn(this,2),this)}makeBasis(e,t,r){return this.set(e.x,t.x,r.x,0,e.y,t.y,r.y,0,e.z,t.z,r.z,0,0,0,0,1),this}extractRotation(e){if(e.determinantAffine()===0)return this.identity();const t=this.elements,r=e.elements,o=1/Js.setFromMatrixColumn(e,0).length(),l=1/Js.setFromMatrixColumn(e,1).length(),d=1/Js.setFromMatrixColumn(e,2).length();return t[0]=r[0]*o,t[1]=r[1]*o,t[2]=r[2]*o,t[3]=0,t[4]=r[4]*l,t[5]=r[5]*l,t[6]=r[6]*l,t[7]=0,t[8]=r[8]*d,t[9]=r[9]*d,t[10]=r[10]*d,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,r=e.x,o=e.y,l=e.z,d=Math.cos(r),f=Math.sin(r),p=Math.cos(o),m=Math.sin(o),_=Math.cos(l),S=Math.sin(l);if(e.order==="XYZ"){const x=d*_,M=d*S,w=f*_,A=f*S;t[0]=p*_,t[4]=-p*S,t[8]=m,t[1]=M+w*m,t[5]=x-A*m,t[9]=-f*p,t[2]=A-x*m,t[6]=w+M*m,t[10]=d*p}else if(e.order==="YXZ"){const x=p*_,M=p*S,w=m*_,A=m*S;t[0]=x+A*f,t[4]=w*f-M,t[8]=d*m,t[1]=d*S,t[5]=d*_,t[9]=-f,t[2]=M*f-w,t[6]=A+x*f,t[10]=d*p}else if(e.order==="ZXY"){const x=p*_,M=p*S,w=m*_,A=m*S;t[0]=x-A*f,t[4]=-d*S,t[8]=w+M*f,t[1]=M+w*f,t[5]=d*_,t[9]=A-x*f,t[2]=-d*m,t[6]=f,t[10]=d*p}else if(e.order==="ZYX"){const x=d*_,M=d*S,w=f*_,A=f*S;t[0]=p*_,t[4]=w*m-M,t[8]=x*m+A,t[1]=p*S,t[5]=A*m+x,t[9]=M*m-w,t[2]=-m,t[6]=f*p,t[10]=d*p}else if(e.order==="YZX"){const x=d*p,M=d*m,w=f*p,A=f*m;t[0]=p*_,t[4]=A-x*S,t[8]=w*S+M,t[1]=S,t[5]=d*_,t[9]=-f*_,t[2]=-m*_,t[6]=M*S+w,t[10]=x-A*S}else if(e.order==="XZY"){const x=d*p,M=d*m,w=f*p,A=f*m;t[0]=p*_,t[4]=-S,t[8]=m*_,t[1]=x*S+A,t[5]=d*_,t[9]=M*S-w,t[2]=w*S-M,t[6]=f*_,t[10]=A*S+x}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(BS,e,VS)}lookAt(e,t,r){const o=this.elements;return ni.subVectors(e,t),ni.lengthSq()===0&&(ni.z=1),ni.normalize(),kr.crossVectors(r,ni),kr.lengthSq()===0&&(Math.abs(r.z)===1?ni.x+=1e-4:ni.z+=1e-4,ni.normalize(),kr.crossVectors(r,ni)),kr.normalize(),zl.crossVectors(ni,kr),o[0]=kr.x,o[4]=zl.x,o[8]=ni.x,o[1]=kr.y,o[5]=zl.y,o[9]=ni.y,o[2]=kr.z,o[6]=zl.z,o[10]=ni.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const r=e.elements,o=t.elements,l=this.elements,d=r[0],f=r[4],p=r[8],m=r[12],_=r[1],S=r[5],x=r[9],M=r[13],w=r[2],A=r[6],v=r[10],y=r[14],P=r[3],U=r[7],N=r[11],L=r[15],R=o[0],D=o[4],E=o[8],I=o[12],z=o[1],B=o[5],H=o[9],ce=o[13],he=o[2],Z=o[6],ue=o[10],K=o[14],q=o[3],se=o[7],le=o[11],k=o[15];return l[0]=d*R+f*z+p*he+m*q,l[4]=d*D+f*B+p*Z+m*se,l[8]=d*E+f*H+p*ue+m*le,l[12]=d*I+f*ce+p*K+m*k,l[1]=_*R+S*z+x*he+M*q,l[5]=_*D+S*B+x*Z+M*se,l[9]=_*E+S*H+x*ue+M*le,l[13]=_*I+S*ce+x*K+M*k,l[2]=w*R+A*z+v*he+y*q,l[6]=w*D+A*B+v*Z+y*se,l[10]=w*E+A*H+v*ue+y*le,l[14]=w*I+A*ce+v*K+y*k,l[3]=P*R+U*z+N*he+L*q,l[7]=P*D+U*B+N*Z+L*se,l[11]=P*E+U*H+N*ue+L*le,l[15]=P*I+U*ce+N*K+L*k,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],r=e[4],o=e[8],l=e[12],d=e[1],f=e[5],p=e[9],m=e[13],_=e[2],S=e[6],x=e[10],M=e[14],w=e[3],A=e[7],v=e[11],y=e[15],P=p*M-m*x,U=f*M-m*S,N=f*x-p*S,L=d*M-m*_,R=d*x-p*_,D=d*S-f*_;return t*(A*P-v*U+y*N)-r*(w*P-v*L+y*R)+o*(w*U-A*L+y*D)-l*(w*N-A*R+v*D)}determinantAffine(){const e=this.elements,t=e[0],r=e[4],o=e[8],l=e[1],d=e[5],f=e[9],p=e[2],m=e[6],_=e[10];return t*(d*_-f*m)-r*(l*_-f*p)+o*(l*m-d*p)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,r){const o=this.elements;return e.isVector3?(o[12]=e.x,o[13]=e.y,o[14]=e.z):(o[12]=e,o[13]=t,o[14]=r),this}invert(){const e=this.elements,t=e[0],r=e[1],o=e[2],l=e[3],d=e[4],f=e[5],p=e[6],m=e[7],_=e[8],S=e[9],x=e[10],M=e[11],w=e[12],A=e[13],v=e[14],y=e[15],P=t*f-r*d,U=t*p-o*d,N=t*m-l*d,L=r*p-o*f,R=r*m-l*f,D=o*m-l*p,E=_*A-S*w,I=_*v-x*w,z=_*y-M*w,B=S*v-x*A,H=S*y-M*A,ce=x*y-M*v,he=P*ce-U*H+N*B+L*z-R*I+D*E;if(he===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const Z=1/he;return e[0]=(f*ce-p*H+m*B)*Z,e[1]=(o*H-r*ce-l*B)*Z,e[2]=(A*D-v*R+y*L)*Z,e[3]=(x*R-S*D-M*L)*Z,e[4]=(p*z-d*ce-m*I)*Z,e[5]=(t*ce-o*z+l*I)*Z,e[6]=(v*N-w*D-y*U)*Z,e[7]=(_*D-x*N+M*U)*Z,e[8]=(d*H-f*z+m*E)*Z,e[9]=(r*z-t*H-l*E)*Z,e[10]=(w*R-A*N+y*P)*Z,e[11]=(S*N-_*R-M*P)*Z,e[12]=(f*I-d*B-p*E)*Z,e[13]=(t*B-r*I+o*E)*Z,e[14]=(A*U-w*L-v*P)*Z,e[15]=(_*L-S*U+x*P)*Z,this}scale(e){const t=this.elements,r=e.x,o=e.y,l=e.z;return t[0]*=r,t[4]*=o,t[8]*=l,t[1]*=r,t[5]*=o,t[9]*=l,t[2]*=r,t[6]*=o,t[10]*=l,t[3]*=r,t[7]*=o,t[11]*=l,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],r=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],o=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,r,o))}makeTranslation(e,t,r){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,r,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),r=Math.sin(e);return this.set(1,0,0,0,0,t,-r,0,0,r,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),r=Math.sin(e);return this.set(t,0,r,0,0,1,0,0,-r,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),r=Math.sin(e);return this.set(t,-r,0,0,r,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const r=Math.cos(t),o=Math.sin(t),l=1-r,d=e.x,f=e.y,p=e.z,m=l*d,_=l*f;return this.set(m*d+r,m*f-o*p,m*p+o*f,0,m*f+o*p,_*f+r,_*p-o*d,0,m*p-o*f,_*p+o*d,l*p*p+r,0,0,0,0,1),this}makeScale(e,t,r){return this.set(e,0,0,0,0,t,0,0,0,0,r,0,0,0,0,1),this}makeShear(e,t,r,o,l,d){return this.set(1,r,l,0,e,1,d,0,t,o,1,0,0,0,0,1),this}compose(e,t,r){const o=this.elements,l=t._x,d=t._y,f=t._z,p=t._w,m=l+l,_=d+d,S=f+f,x=l*m,M=l*_,w=l*S,A=d*_,v=d*S,y=f*S,P=p*m,U=p*_,N=p*S,L=r.x,R=r.y,D=r.z;return o[0]=(1-(A+y))*L,o[1]=(M+N)*L,o[2]=(w-U)*L,o[3]=0,o[4]=(M-N)*R,o[5]=(1-(x+y))*R,o[6]=(v+P)*R,o[7]=0,o[8]=(w+U)*D,o[9]=(v-P)*D,o[10]=(1-(x+A))*D,o[11]=0,o[12]=e.x,o[13]=e.y,o[14]=e.z,o[15]=1,this}decompose(e,t,r){const o=this.elements;e.x=o[12],e.y=o[13],e.z=o[14];const l=this.determinantAffine();if(l===0)return r.set(1,1,1),t.identity(),this;let d=Js.set(o[0],o[1],o[2]).length();const f=Js.set(o[4],o[5],o[6]).length(),p=Js.set(o[8],o[9],o[10]).length();l<0&&(d=-d),Ei.copy(this);const m=1/d,_=1/f,S=1/p;return Ei.elements[0]*=m,Ei.elements[1]*=m,Ei.elements[2]*=m,Ei.elements[4]*=_,Ei.elements[5]*=_,Ei.elements[6]*=_,Ei.elements[8]*=S,Ei.elements[9]*=S,Ei.elements[10]*=S,t.setFromRotationMatrix(Ei),r.x=d,r.y=f,r.z=p,this}makePerspective(e,t,r,o,l,d,f=zi,p=!1){const m=this.elements,_=2*l/(t-e),S=2*l/(r-o),x=(t+e)/(t-e),M=(r+o)/(r-o);let w,A;if(p)w=l/(d-l),A=d*l/(d-l);else if(f===zi)w=-(d+l)/(d-l),A=-2*d*l/(d-l);else if(f===bc)w=-d/(d-l),A=-d*l/(d-l);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+f);return m[0]=_,m[4]=0,m[8]=x,m[12]=0,m[1]=0,m[5]=S,m[9]=M,m[13]=0,m[2]=0,m[6]=0,m[10]=w,m[14]=A,m[3]=0,m[7]=0,m[11]=-1,m[15]=0,this}makeOrthographic(e,t,r,o,l,d,f=zi,p=!1){const m=this.elements,_=2/(t-e),S=2/(r-o),x=-(t+e)/(t-e),M=-(r+o)/(r-o);let w,A;if(p)w=1/(d-l),A=d/(d-l);else if(f===zi)w=-2/(d-l),A=-(d+l)/(d-l);else if(f===bc)w=-1/(d-l),A=-l/(d-l);else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+f);return m[0]=_,m[4]=0,m[8]=0,m[12]=x,m[1]=0,m[5]=S,m[9]=0,m[13]=M,m[2]=0,m[6]=0,m[10]=w,m[14]=A,m[3]=0,m[7]=0,m[11]=0,m[15]=1,this}equals(e){const t=this.elements,r=e.elements;for(let o=0;o<16;o++)if(t[o]!==r[o])return!1;return!0}fromArray(e,t=0){for(let r=0;r<16;r++)this.elements[r]=e[r+t];return this}toArray(e=[],t=0){const r=this.elements;return e[t]=r[0],e[t+1]=r[1],e[t+2]=r[2],e[t+3]=r[3],e[t+4]=r[4],e[t+5]=r[5],e[t+6]=r[6],e[t+7]=r[7],e[t+8]=r[8],e[t+9]=r[9],e[t+10]=r[10],e[t+11]=r[11],e[t+12]=r[12],e[t+13]=r[13],e[t+14]=r[14],e[t+15]=r[15],e}};Cc.prototype.isMatrix4=!0;let en=Cc;const Js=new Y,Ei=new en,BS=new Y(0,0,0),VS=new Y(1,1,1),kr=new Y,zl=new Y,ni=new Y,lg=new en,cg=new Ea;class Es{constructor(e=0,t=0,r=0,o=Es.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=r,this._order=o}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,r,o=this._order){return this._x=e,this._y=t,this._z=r,this._order=o,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,r=!0){const o=e.elements,l=o[0],d=o[4],f=o[8],p=o[1],m=o[5],_=o[9],S=o[2],x=o[6],M=o[10];switch(t){case"XYZ":this._y=Math.asin(vt(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(-_,M),this._z=Math.atan2(-d,l)):(this._x=Math.atan2(x,m),this._z=0);break;case"YXZ":this._x=Math.asin(-vt(_,-1,1)),Math.abs(_)<.9999999?(this._y=Math.atan2(f,M),this._z=Math.atan2(p,m)):(this._y=Math.atan2(-S,l),this._z=0);break;case"ZXY":this._x=Math.asin(vt(x,-1,1)),Math.abs(x)<.9999999?(this._y=Math.atan2(-S,M),this._z=Math.atan2(-d,m)):(this._y=0,this._z=Math.atan2(p,l));break;case"ZYX":this._y=Math.asin(-vt(S,-1,1)),Math.abs(S)<.9999999?(this._x=Math.atan2(x,M),this._z=Math.atan2(p,l)):(this._x=0,this._z=Math.atan2(-d,m));break;case"YZX":this._z=Math.asin(vt(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(-_,m),this._y=Math.atan2(-S,l)):(this._x=0,this._y=Math.atan2(f,M));break;case"XZY":this._z=Math.asin(-vt(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(x,m),this._y=Math.atan2(f,l)):(this._x=Math.atan2(-_,M),this._y=0);break;default:rt("Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,r===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,r){return lg.makeRotationFromQuaternion(e),this.setFromRotationMatrix(lg,t,r)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return cg.setFromEuler(this),this.setFromQuaternion(cg,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Es.DEFAULT_ORDER="XYZ";class Dx{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let HS=0;const ug=new Y,ea=new Ea,er=new en,Bl=new Y,po=new Y,jS=new Y,GS=new Ea,dg=new Y(1,0,0),fg=new Y(0,1,0),hg=new Y(0,0,1),pg={type:"added"},WS={type:"removed"},ta={type:"childadded",child:null},Rd={type:"childremoved",child:null};class Bn extends ws{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:HS++}),this.uuid=Ao(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Bn.DEFAULT_UP.clone();const e=new Y,t=new Es,r=new Ea,o=new Y(1,1,1);function l(){r.setFromEuler(t,!1)}function d(){t.setFromQuaternion(r,void 0,!1)}t._onChange(l),r._onChange(d),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:r},scale:{configurable:!0,enumerable:!0,value:o},modelViewMatrix:{value:new en},normalMatrix:{value:new ut}}),this.matrix=new en,this.matrixWorld=new en,this.matrixAutoUpdate=Bn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Bn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Dx,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.static=!1,this.userData={},this.pivot=null}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return ea.setFromAxisAngle(e,t),this.quaternion.multiply(ea),this}rotateOnWorldAxis(e,t){return ea.setFromAxisAngle(e,t),this.quaternion.premultiply(ea),this}rotateX(e){return this.rotateOnAxis(dg,e)}rotateY(e){return this.rotateOnAxis(fg,e)}rotateZ(e){return this.rotateOnAxis(hg,e)}translateOnAxis(e,t){return ug.copy(e).applyQuaternion(this.quaternion),this.position.add(ug.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(dg,e)}translateY(e){return this.translateOnAxis(fg,e)}translateZ(e){return this.translateOnAxis(hg,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(er.copy(this.matrixWorld).invert())}lookAt(e,t,r){e.isVector3?Bl.copy(e):Bl.set(e,t,r);const o=this.parent;this.updateWorldMatrix(!0,!1),po.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?er.lookAt(po,Bl,this.up):er.lookAt(Bl,po,this.up),this.quaternion.setFromRotationMatrix(er),o&&(er.extractRotation(o.matrixWorld),ea.setFromRotationMatrix(er),this.quaternion.premultiply(ea.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(wt("Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(pg),ta.child=e,this.dispatchEvent(ta),ta.child=null):wt("Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let r=0;r<arguments.length;r++)this.remove(arguments[r]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(WS),Rd.child=e,this.dispatchEvent(Rd),Rd.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),er.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),er.multiply(e.parent.matrixWorld)),e.applyMatrix4(er),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(pg),ta.child=e,this.dispatchEvent(ta),ta.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let r=0,o=this.children.length;r<o;r++){const d=this.children[r].getObjectByProperty(e,t);if(d!==void 0)return d}}getObjectsByProperty(e,t,r=[]){this[e]===t&&r.push(this);const o=this.children;for(let l=0,d=o.length;l<d;l++)o[l].getObjectsByProperty(e,t,r);return r}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(po,e,jS),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(po,GS,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let r=0,o=t.length;r<o;r++)t[r].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let r=0,o=t.length;r<o;r++)t[r].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale);const e=this.pivot;if(e!==null){const t=e.x,r=e.y,o=e.z,l=this.matrix.elements;l[12]+=t-l[0]*t-l[4]*r-l[8]*o,l[13]+=r-l[1]*t-l[5]*r-l[9]*o,l[14]+=o-l[2]*t-l[6]*r-l[10]*o}this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let r=0,o=t.length;r<o;r++)t[r].updateMatrixWorld(e)}updateWorldMatrix(e,t,r=!1){const o=this.parent;if(e===!0&&o!==null&&o.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||r)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,r=!0),t===!0){const l=this.children;for(let d=0,f=l.length;d<f;d++)l[d].updateWorldMatrix(!1,!0,r)}}toJSON(e){const t=e===void 0||typeof e=="string",r={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},r.metadata={version:4.7,type:"Object",generator:"Object3D.toJSON"});const o={};o.uuid=this.uuid,o.type=this.type,this.name!==""&&(o.name=this.name),this.castShadow===!0&&(o.castShadow=!0),this.receiveShadow===!0&&(o.receiveShadow=!0),this.visible===!1&&(o.visible=!1),this.frustumCulled===!1&&(o.frustumCulled=!1),this.renderOrder!==0&&(o.renderOrder=this.renderOrder),this.static!==!1&&(o.static=this.static),Object.keys(this.userData).length>0&&(o.userData=this.userData),o.layers=this.layers.mask,o.matrix=this.matrix.toArray(),o.up=this.up.toArray(),this.pivot!==null&&(o.pivot=this.pivot.toArray()),this.matrixAutoUpdate===!1&&(o.matrixAutoUpdate=!1),this.morphTargetDictionary!==void 0&&(o.morphTargetDictionary=Object.assign({},this.morphTargetDictionary)),this.morphTargetInfluences!==void 0&&(o.morphTargetInfluences=this.morphTargetInfluences.slice()),this.isInstancedMesh&&(o.type="InstancedMesh",o.count=this.count,o.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(o.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(o.type="BatchedMesh",o.perObjectFrustumCulled=this.perObjectFrustumCulled,o.sortObjects=this.sortObjects,o.drawRanges=this._drawRanges,o.reservedRanges=this._reservedRanges,o.geometryInfo=this._geometryInfo.map(f=>({...f,boundingBox:f.boundingBox?f.boundingBox.toJSON():void 0,boundingSphere:f.boundingSphere?f.boundingSphere.toJSON():void 0})),o.instanceInfo=this._instanceInfo.map(f=>({...f})),o.availableInstanceIds=this._availableInstanceIds.slice(),o.availableGeometryIds=this._availableGeometryIds.slice(),o.nextIndexStart=this._nextIndexStart,o.nextVertexStart=this._nextVertexStart,o.geometryCount=this._geometryCount,o.maxInstanceCount=this._maxInstanceCount,o.maxVertexCount=this._maxVertexCount,o.maxIndexCount=this._maxIndexCount,o.geometryInitialized=this._geometryInitialized,o.matricesTexture=this._matricesTexture.toJSON(e),o.indirectTexture=this._indirectTexture.toJSON(e),this._colorsTexture!==null&&(o.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(o.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(o.boundingBox=this.boundingBox.toJSON()));function l(f,p){return f[p.uuid]===void 0&&(f[p.uuid]=p.toJSON(e)),p.uuid}if(this.isScene)this.background&&(this.background.isColor?o.background=this.background.toJSON():this.background.isTexture&&(o.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(o.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){o.geometry=l(e.geometries,this.geometry);const f=this.geometry.parameters;if(f!==void 0&&f.shapes!==void 0){const p=f.shapes;if(Array.isArray(p))for(let m=0,_=p.length;m<_;m++){const S=p[m];l(e.shapes,S)}else l(e.shapes,p)}}if(this.isSkinnedMesh&&(o.bindMode=this.bindMode,o.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(l(e.skeletons,this.skeleton),o.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const f=[];for(let p=0,m=this.material.length;p<m;p++)f.push(l(e.materials,this.material[p]));o.material=f}else o.material=l(e.materials,this.material);if(this.children.length>0){o.children=[];for(let f=0;f<this.children.length;f++)o.children.push(this.children[f].toJSON(e).object)}if(this.animations.length>0){o.animations=[];for(let f=0;f<this.animations.length;f++){const p=this.animations[f];o.animations.push(l(e.animations,p))}}if(t){const f=d(e.geometries),p=d(e.materials),m=d(e.textures),_=d(e.images),S=d(e.shapes),x=d(e.skeletons),M=d(e.animations),w=d(e.nodes);f.length>0&&(r.geometries=f),p.length>0&&(r.materials=p),m.length>0&&(r.textures=m),_.length>0&&(r.images=_),S.length>0&&(r.shapes=S),x.length>0&&(r.skeletons=x),M.length>0&&(r.animations=M),w.length>0&&(r.nodes=w)}return r.object=o,r;function d(f){const p=[];for(const m in f){const _=f[m];delete _.metadata,p.push(_)}return p}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.pivot=e.pivot!==null?e.pivot.clone():null,this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.static=e.static,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let r=0;r<e.children.length;r++){const o=e.children[r];this.add(o.clone())}return this}}Bn.DEFAULT_UP=new Y(0,1,0);Bn.DEFAULT_MATRIX_AUTO_UPDATE=!0;Bn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;class Mo extends Bn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const XS={type:"move"};class Pd{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Mo,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Mo,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new Y,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new Y),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Mo,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new Y,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new Y,this._grip.eventsEnabled=!1),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const r of e.hand.values())this._getHandJoint(t,r)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,r){let o=null,l=null,d=null;const f=this._targetRay,p=this._grip,m=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(m&&e.hand){d=!0;for(const A of e.hand.values()){const v=t.getJointPose(A,r),y=this._getHandJoint(m,A);v!==null&&(y.matrix.fromArray(v.transform.matrix),y.matrix.decompose(y.position,y.rotation,y.scale),y.matrixWorldNeedsUpdate=!0,y.jointRadius=v.radius),y.visible=v!==null}const _=m.joints["index-finger-tip"],S=m.joints["thumb-tip"],x=_.position.distanceTo(S.position),M=.02,w=.005;m.inputState.pinching&&x>M+w?(m.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!m.inputState.pinching&&x<=M-w&&(m.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else p!==null&&e.gripSpace&&(l=t.getPose(e.gripSpace,r),l!==null&&(p.matrix.fromArray(l.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,l.linearVelocity?(p.hasLinearVelocity=!0,p.linearVelocity.copy(l.linearVelocity)):p.hasLinearVelocity=!1,l.angularVelocity?(p.hasAngularVelocity=!0,p.angularVelocity.copy(l.angularVelocity)):p.hasAngularVelocity=!1,p.eventsEnabled&&p.dispatchEvent({type:"gripUpdated",data:e,target:this})));f!==null&&(o=t.getPose(e.targetRaySpace,r),o===null&&l!==null&&(o=l),o!==null&&(f.matrix.fromArray(o.transform.matrix),f.matrix.decompose(f.position,f.rotation,f.scale),f.matrixWorldNeedsUpdate=!0,o.linearVelocity?(f.hasLinearVelocity=!0,f.linearVelocity.copy(o.linearVelocity)):f.hasLinearVelocity=!1,o.angularVelocity?(f.hasAngularVelocity=!0,f.angularVelocity.copy(o.angularVelocity)):f.hasAngularVelocity=!1,this.dispatchEvent(XS)))}return f!==null&&(f.visible=o!==null),p!==null&&(p.visible=l!==null),m!==null&&(m.visible=d!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const r=new Mo;r.matrixAutoUpdate=!1,r.visible=!1,e.joints[t.jointName]=r,e.add(r)}return e.joints[t.jointName]}}const Ux={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Or={h:0,s:0,l:0},Vl={h:0,s:0,l:0};function Ld(s,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?s+(e-s)*6*t:t<1/2?e:t<2/3?s+(e-s)*6*(2/3-t):s}class Ct{constructor(e,t,r){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,r)}set(e,t,r){if(t===void 0&&r===void 0){const o=e;o&&o.isColor?this.copy(o):typeof o=="number"?this.setHex(o):typeof o=="string"&&this.setStyle(o)}else this.setRGB(e,t,r);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=fi){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,St.colorSpaceToWorking(this,t),this}setRGB(e,t,r,o=St.workingColorSpace){return this.r=e,this.g=t,this.b=r,St.colorSpaceToWorking(this,o),this}setHSL(e,t,r,o=St.workingColorSpace){if(e=IS(e,1),t=vt(t,0,1),r=vt(r,0,1),t===0)this.r=this.g=this.b=r;else{const l=r<=.5?r*(1+t):r+t-r*t,d=2*r-l;this.r=Ld(d,l,e+1/3),this.g=Ld(d,l,e),this.b=Ld(d,l,e-1/3)}return St.colorSpaceToWorking(this,o),this}setStyle(e,t=fi){function r(l){l!==void 0&&parseFloat(l)<1&&rt("Color: Alpha component of "+e+" will be ignored.")}let o;if(o=/^(\w+)\(([^\)]*)\)/.exec(e)){let l;const d=o[1],f=o[2];switch(d){case"rgb":case"rgba":if(l=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(f))return r(l[4]),this.setRGB(Math.min(255,parseInt(l[1],10))/255,Math.min(255,parseInt(l[2],10))/255,Math.min(255,parseInt(l[3],10))/255,t);if(l=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(f))return r(l[4]),this.setRGB(Math.min(100,parseInt(l[1],10))/100,Math.min(100,parseInt(l[2],10))/100,Math.min(100,parseInt(l[3],10))/100,t);break;case"hsl":case"hsla":if(l=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(f))return r(l[4]),this.setHSL(parseFloat(l[1])/360,parseFloat(l[2])/100,parseFloat(l[3])/100,t);break;default:rt("Color: Unknown color model "+e)}}else if(o=/^\#([A-Fa-f\d]+)$/.exec(e)){const l=o[1],d=l.length;if(d===3)return this.setRGB(parseInt(l.charAt(0),16)/15,parseInt(l.charAt(1),16)/15,parseInt(l.charAt(2),16)/15,t);if(d===6)return this.setHex(parseInt(l,16),t);rt("Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=fi){const r=Ux[e.toLowerCase()];return r!==void 0?this.setHex(r,t):rt("Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=lr(e.r),this.g=lr(e.g),this.b=lr(e.b),this}copyLinearToSRGB(e){return this.r=pa(e.r),this.g=pa(e.g),this.b=pa(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=fi){return St.workingToColorSpace(Ln.copy(this),e),Math.round(vt(Ln.r*255,0,255))*65536+Math.round(vt(Ln.g*255,0,255))*256+Math.round(vt(Ln.b*255,0,255))}getHexString(e=fi){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=St.workingColorSpace){St.workingToColorSpace(Ln.copy(this),t);const r=Ln.r,o=Ln.g,l=Ln.b,d=Math.max(r,o,l),f=Math.min(r,o,l);let p,m;const _=(f+d)/2;if(f===d)p=0,m=0;else{const S=d-f;switch(m=_<=.5?S/(d+f):S/(2-d-f),d){case r:p=(o-l)/S+(o<l?6:0);break;case o:p=(l-r)/S+2;break;case l:p=(r-o)/S+4;break}p/=6}return e.h=p,e.s=m,e.l=_,e}getRGB(e,t=St.workingColorSpace){return St.workingToColorSpace(Ln.copy(this),t),e.r=Ln.r,e.g=Ln.g,e.b=Ln.b,e}getStyle(e=fi){St.workingToColorSpace(Ln.copy(this),e);const t=Ln.r,r=Ln.g,o=Ln.b;return e!==fi?`color(${e} ${t.toFixed(3)} ${r.toFixed(3)} ${o.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(r*255)},${Math.round(o*255)})`}offsetHSL(e,t,r){return this.getHSL(Or),this.setHSL(Or.h+e,Or.s+t,Or.l+r)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,r){return this.r=e.r+(t.r-e.r)*r,this.g=e.g+(t.g-e.g)*r,this.b=e.b+(t.b-e.b)*r,this}lerpHSL(e,t){this.getHSL(Or),e.getHSL(Vl);const r=wd(Or.h,Vl.h,t),o=wd(Or.s,Vl.s,t),l=wd(Or.l,Vl.l,t);return this.setHSL(r,o,l),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,r=this.g,o=this.b,l=e.elements;return this.r=l[0]*t+l[3]*r+l[6]*o,this.g=l[1]*t+l[4]*r+l[7]*o,this.b=l[2]*t+l[5]*r+l[8]*o,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Ln=new Ct;Ct.NAMES=Ux;class qS extends Bn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Es,this.environmentIntensity=1,this.environmentRotation=new Es,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}const wi=new Y,tr=new Y,Id=new Y,nr=new Y,na=new Y,ia=new Y,mg=new Y,Dd=new Y,Ud=new Y,Fd=new Y,kd=new sn,Od=new sn,zd=new sn;class Ai{constructor(e=new Y,t=new Y,r=new Y){this.a=e,this.b=t,this.c=r}static getNormal(e,t,r,o){o.subVectors(r,t),wi.subVectors(e,t),o.cross(wi);const l=o.lengthSq();return l>0?o.multiplyScalar(1/Math.sqrt(l)):o.set(0,0,0)}static getBarycoord(e,t,r,o,l){wi.subVectors(o,t),tr.subVectors(r,t),Id.subVectors(e,t);const d=wi.dot(wi),f=wi.dot(tr),p=wi.dot(Id),m=tr.dot(tr),_=tr.dot(Id),S=d*m-f*f;if(S===0)return l.set(0,0,0),null;const x=1/S,M=(m*p-f*_)*x,w=(d*_-f*p)*x;return l.set(1-M-w,w,M)}static containsPoint(e,t,r,o){return this.getBarycoord(e,t,r,o,nr)===null?!1:nr.x>=0&&nr.y>=0&&nr.x+nr.y<=1}static getInterpolation(e,t,r,o,l,d,f,p){return this.getBarycoord(e,t,r,o,nr)===null?(p.x=0,p.y=0,"z"in p&&(p.z=0),"w"in p&&(p.w=0),null):(p.setScalar(0),p.addScaledVector(l,nr.x),p.addScaledVector(d,nr.y),p.addScaledVector(f,nr.z),p)}static getInterpolatedAttribute(e,t,r,o,l,d){return kd.setScalar(0),Od.setScalar(0),zd.setScalar(0),kd.fromBufferAttribute(e,t),Od.fromBufferAttribute(e,r),zd.fromBufferAttribute(e,o),d.setScalar(0),d.addScaledVector(kd,l.x),d.addScaledVector(Od,l.y),d.addScaledVector(zd,l.z),d}static isFrontFacing(e,t,r,o){return wi.subVectors(r,t),tr.subVectors(e,t),wi.cross(tr).dot(o)<0}set(e,t,r){return this.a.copy(e),this.b.copy(t),this.c.copy(r),this}setFromPointsAndIndices(e,t,r,o){return this.a.copy(e[t]),this.b.copy(e[r]),this.c.copy(e[o]),this}setFromAttributeAndIndices(e,t,r,o){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,r),this.c.fromBufferAttribute(e,o),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return wi.subVectors(this.c,this.b),tr.subVectors(this.a,this.b),wi.cross(tr).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Ai.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Ai.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,r,o,l){return Ai.getInterpolation(e,this.a,this.b,this.c,t,r,o,l)}containsPoint(e){return Ai.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Ai.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const r=this.a,o=this.b,l=this.c;let d,f;na.subVectors(o,r),ia.subVectors(l,r),Dd.subVectors(e,r);const p=na.dot(Dd),m=ia.dot(Dd);if(p<=0&&m<=0)return t.copy(r);Ud.subVectors(e,o);const _=na.dot(Ud),S=ia.dot(Ud);if(_>=0&&S<=_)return t.copy(o);const x=p*S-_*m;if(x<=0&&p>=0&&_<=0)return d=p/(p-_),t.copy(r).addScaledVector(na,d);Fd.subVectors(e,l);const M=na.dot(Fd),w=ia.dot(Fd);if(w>=0&&M<=w)return t.copy(l);const A=M*m-p*w;if(A<=0&&m>=0&&w<=0)return f=m/(m-w),t.copy(r).addScaledVector(ia,f);const v=_*w-M*S;if(v<=0&&S-_>=0&&M-w>=0)return mg.subVectors(l,o),f=(S-_)/(S-_+(M-w)),t.copy(o).addScaledVector(mg,f);const y=1/(v+A+x);return d=A*y,f=x*y,t.copy(r).addScaledVector(na,d).addScaledVector(ia,f)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}class Co{constructor(e=new Y(1/0,1/0,1/0),t=new Y(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,r=e.length;t<r;t+=3)this.expandByPoint(Ti.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,r=e.count;t<r;t++)this.expandByPoint(Ti.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,r=e.length;t<r;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const r=Ti.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(r),this.max.copy(e).add(r),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const r=e.geometry;if(r!==void 0){const l=r.getAttribute("position");if(t===!0&&l!==void 0&&e.isInstancedMesh!==!0)for(let d=0,f=l.count;d<f;d++)e.isMesh===!0?e.getVertexPosition(d,Ti):Ti.fromBufferAttribute(l,d),Ti.applyMatrix4(e.matrixWorld),this.expandByPoint(Ti);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Hl.copy(e.boundingBox)):(r.boundingBox===null&&r.computeBoundingBox(),Hl.copy(r.boundingBox)),Hl.applyMatrix4(e.matrixWorld),this.union(Hl)}const o=e.children;for(let l=0,d=o.length;l<d;l++)this.expandByObject(o[l],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,Ti),Ti.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,r;return e.normal.x>0?(t=e.normal.x*this.min.x,r=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,r=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,r+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,r+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,r+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,r+=e.normal.z*this.min.z),t<=-e.constant&&r>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(mo),jl.subVectors(this.max,mo),ra.subVectors(e.a,mo),sa.subVectors(e.b,mo),aa.subVectors(e.c,mo),zr.subVectors(sa,ra),Br.subVectors(aa,sa),hs.subVectors(ra,aa);let t=[0,-zr.z,zr.y,0,-Br.z,Br.y,0,-hs.z,hs.y,zr.z,0,-zr.x,Br.z,0,-Br.x,hs.z,0,-hs.x,-zr.y,zr.x,0,-Br.y,Br.x,0,-hs.y,hs.x,0];return!Bd(t,ra,sa,aa,jl)||(t=[1,0,0,0,1,0,0,0,1],!Bd(t,ra,sa,aa,jl))?!1:(Gl.crossVectors(zr,Br),t=[Gl.x,Gl.y,Gl.z],Bd(t,ra,sa,aa,jl))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,Ti).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(Ti).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(ir[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),ir[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),ir[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),ir[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),ir[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),ir[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),ir[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),ir[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(ir),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(e){return this.min.fromArray(e.min),this.max.fromArray(e.max),this}}const ir=[new Y,new Y,new Y,new Y,new Y,new Y,new Y,new Y],Ti=new Y,Hl=new Co,ra=new Y,sa=new Y,aa=new Y,zr=new Y,Br=new Y,hs=new Y,mo=new Y,jl=new Y,Gl=new Y,ps=new Y;function Bd(s,e,t,r,o){for(let l=0,d=s.length-3;l<=d;l+=3){ps.fromArray(s,l);const f=o.x*Math.abs(ps.x)+o.y*Math.abs(ps.y)+o.z*Math.abs(ps.z),p=e.dot(ps),m=t.dot(ps),_=r.dot(ps);if(Math.max(-Math.max(p,m,_),Math.min(p,m,_))>f)return!1}return!0}const cn=new Y,Wl=new yt;let YS=0;class Ni extends ws{constructor(e,t,r=!1){if(super(),Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:YS++}),this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=r,this.usage=tg,this.updateRanges=[],this.gpuType=Oi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,r){e*=this.itemSize,r*=t.itemSize;for(let o=0,l=this.itemSize;o<l;o++)this.array[e+o]=t.array[r+o];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,r=this.count;t<r;t++)Wl.fromBufferAttribute(this,t),Wl.applyMatrix3(e),this.setXY(t,Wl.x,Wl.y);else if(this.itemSize===3)for(let t=0,r=this.count;t<r;t++)cn.fromBufferAttribute(this,t),cn.applyMatrix3(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}applyMatrix4(e){for(let t=0,r=this.count;t<r;t++)cn.fromBufferAttribute(this,t),cn.applyMatrix4(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}applyNormalMatrix(e){for(let t=0,r=this.count;t<r;t++)cn.fromBufferAttribute(this,t),cn.applyNormalMatrix(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}transformDirection(e){for(let t=0,r=this.count;t<r;t++)cn.fromBufferAttribute(this,t),cn.transformDirection(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let r=this.array[e*this.itemSize+t];return this.normalized&&(r=ho(r,this.array)),r}setComponent(e,t,r){return this.normalized&&(r=Kn(r,this.array)),this.array[e*this.itemSize+t]=r,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=ho(t,this.array)),t}setX(e,t){return this.normalized&&(t=Kn(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=ho(t,this.array)),t}setY(e,t){return this.normalized&&(t=Kn(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=ho(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Kn(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=ho(t,this.array)),t}setW(e,t){return this.normalized&&(t=Kn(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,r){return e*=this.itemSize,this.normalized&&(t=Kn(t,this.array),r=Kn(r,this.array)),this.array[e+0]=t,this.array[e+1]=r,this}setXYZ(e,t,r,o){return e*=this.itemSize,this.normalized&&(t=Kn(t,this.array),r=Kn(r,this.array),o=Kn(o,this.array)),this.array[e+0]=t,this.array[e+1]=r,this.array[e+2]=o,this}setXYZW(e,t,r,o,l){return e*=this.itemSize,this.normalized&&(t=Kn(t,this.array),r=Kn(r,this.array),o=Kn(o,this.array),l=Kn(l,this.array)),this.array[e+0]=t,this.array[e+1]=r,this.array[e+2]=o,this.array[e+3]=l,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==tg&&(e.usage=this.usage),e}dispose(){this.dispatchEvent({type:"dispose"})}}class Fx extends Ni{constructor(e,t,r){super(new Uint16Array(e),t,r)}}class kx extends Ni{constructor(e,t,r){super(new Uint32Array(e),t,r)}}class Dn extends Ni{constructor(e,t,r){super(new Float32Array(e),t,r)}}const $S=new Co,go=new Y,Vd=new Y;class No{constructor(e=new Y,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const r=this.center;t!==void 0?r.copy(t):$S.setFromPoints(e).getCenter(r);let o=0;for(let l=0,d=e.length;l<d;l++)o=Math.max(o,r.distanceToSquared(e[l]));return this.radius=Math.sqrt(o),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const r=this.center.distanceToSquared(e);return t.copy(e),r>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;go.subVectors(e,this.center);const t=go.lengthSq();if(t>this.radius*this.radius){const r=Math.sqrt(t),o=(r-this.radius)*.5;this.center.addScaledVector(go,o/r),this.radius+=o}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Vd.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(go.copy(e.center).add(Vd)),this.expandByPoint(go.copy(e.center).sub(Vd))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(e){return this.radius=e.radius,this.center.fromArray(e.center),this}}let KS=0;const di=new en,Hd=new Bn,oa=new Y,ii=new Co,xo=new Co,vn=new Y;class Vn extends ws{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:KS++}),this.uuid=Ao(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.indirectOffset=0,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={},this._transformed=!1}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(NS(e)?kx:Fx)(e,1):this.index=e,this}setIndirect(e,t=0){return this.indirect=e,this.indirectOffset=t,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,r=0){this.groups.push({start:e,count:t,materialIndex:r})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const r=this.attributes.normal;if(r!==void 0){const l=new ut().getNormalMatrix(e);r.applyNormalMatrix(l),r.needsUpdate=!0}const o=this.attributes.tangent;return o!==void 0&&(o.transformDirection(e),o.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this._transformed=!0,this}applyQuaternion(e){return di.makeRotationFromQuaternion(e),this.applyMatrix4(di),this}rotateX(e){return di.makeRotationX(e),this.applyMatrix4(di),this}rotateY(e){return di.makeRotationY(e),this.applyMatrix4(di),this}rotateZ(e){return di.makeRotationZ(e),this.applyMatrix4(di),this}translate(e,t,r){return di.makeTranslation(e,t,r),this.applyMatrix4(di),this}scale(e,t,r){return di.makeScale(e,t,r),this.applyMatrix4(di),this}lookAt(e){return Hd.lookAt(e),Hd.updateMatrix(),this.applyMatrix4(Hd.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(oa).negate(),this.translate(oa.x,oa.y,oa.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const r=[];for(let o=0,l=e.length;o<l;o++){const d=e[o];r.push(d.x,d.y,d.z||0)}this.setAttribute("position",new Dn(r,3))}else{const r=Math.min(e.length,t.count);for(let o=0;o<r;o++){const l=e[o];t.setXYZ(o,l.x,l.y,l.z||0)}e.length>t.count&&rt("BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Co);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){wt("BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new Y(-1/0,-1/0,-1/0),new Y(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let r=0,o=t.length;r<o;r++){const l=t[r];ii.setFromBufferAttribute(l),this.morphTargetsRelative?(vn.addVectors(this.boundingBox.min,ii.min),this.boundingBox.expandByPoint(vn),vn.addVectors(this.boundingBox.max,ii.max),this.boundingBox.expandByPoint(vn)):(this.boundingBox.expandByPoint(ii.min),this.boundingBox.expandByPoint(ii.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&wt('BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new No);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){wt("BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new Y,1/0);return}if(e){const r=this.boundingSphere.center;if(ii.setFromBufferAttribute(e),t)for(let l=0,d=t.length;l<d;l++){const f=t[l];xo.setFromBufferAttribute(f),this.morphTargetsRelative?(vn.addVectors(ii.min,xo.min),ii.expandByPoint(vn),vn.addVectors(ii.max,xo.max),ii.expandByPoint(vn)):(ii.expandByPoint(xo.min),ii.expandByPoint(xo.max))}ii.getCenter(r);let o=0;for(let l=0,d=e.count;l<d;l++)vn.fromBufferAttribute(e,l),o=Math.max(o,r.distanceToSquared(vn));if(t)for(let l=0,d=t.length;l<d;l++){const f=t[l],p=this.morphTargetsRelative;for(let m=0,_=f.count;m<_;m++)vn.fromBufferAttribute(f,m),p&&(oa.fromBufferAttribute(e,m),vn.add(oa)),o=Math.max(o,r.distanceToSquared(vn))}this.boundingSphere.radius=Math.sqrt(o),isNaN(this.boundingSphere.radius)&&wt('BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){wt("BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const r=t.position,o=t.normal,l=t.uv;let d=this.getAttribute("tangent");(d===void 0||d.count!==r.count)&&(d=new Ni(new Float32Array(4*r.count),4),this.setAttribute("tangent",d));const f=[],p=[];for(let E=0;E<r.count;E++)f[E]=new Y,p[E]=new Y;const m=new Y,_=new Y,S=new Y,x=new yt,M=new yt,w=new yt,A=new Y,v=new Y;function y(E,I,z){m.fromBufferAttribute(r,E),_.fromBufferAttribute(r,I),S.fromBufferAttribute(r,z),x.fromBufferAttribute(l,E),M.fromBufferAttribute(l,I),w.fromBufferAttribute(l,z),_.sub(m),S.sub(m),M.sub(x),w.sub(x);const B=1/(M.x*w.y-w.x*M.y);isFinite(B)&&(A.copy(_).multiplyScalar(w.y).addScaledVector(S,-M.y).multiplyScalar(B),v.copy(S).multiplyScalar(M.x).addScaledVector(_,-w.x).multiplyScalar(B),f[E].add(A),f[I].add(A),f[z].add(A),p[E].add(v),p[I].add(v),p[z].add(v))}let P=this.groups;P.length===0&&(P=[{start:0,count:e.count}]);for(let E=0,I=P.length;E<I;++E){const z=P[E],B=z.start,H=z.count;for(let ce=B,he=B+H;ce<he;ce+=3)y(e.getX(ce+0),e.getX(ce+1),e.getX(ce+2))}const U=new Y,N=new Y,L=new Y,R=new Y;function D(E){L.fromBufferAttribute(o,E),R.copy(L);const I=f[E];U.copy(I),U.sub(L.multiplyScalar(L.dot(I))).normalize(),N.crossVectors(R,I);const B=N.dot(p[E])<0?-1:1;d.setXYZW(E,U.x,U.y,U.z,B)}for(let E=0,I=P.length;E<I;++E){const z=P[E],B=z.start,H=z.count;for(let ce=B,he=B+H;ce<he;ce+=3)D(e.getX(ce+0)),D(e.getX(ce+1)),D(e.getX(ce+2))}this._transformed=!0}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let r=this.getAttribute("normal");if(r===void 0||r.count!==t.count)r=new Ni(new Float32Array(t.count*3),3),this.setAttribute("normal",r);else for(let x=0,M=r.count;x<M;x++)r.setXYZ(x,0,0,0);const o=new Y,l=new Y,d=new Y,f=new Y,p=new Y,m=new Y,_=new Y,S=new Y;if(e)for(let x=0,M=e.count;x<M;x+=3){const w=e.getX(x+0),A=e.getX(x+1),v=e.getX(x+2);o.fromBufferAttribute(t,w),l.fromBufferAttribute(t,A),d.fromBufferAttribute(t,v),_.subVectors(d,l),S.subVectors(o,l),_.cross(S),f.fromBufferAttribute(r,w),p.fromBufferAttribute(r,A),m.fromBufferAttribute(r,v),f.add(_),p.add(_),m.add(_),r.setXYZ(w,f.x,f.y,f.z),r.setXYZ(A,p.x,p.y,p.z),r.setXYZ(v,m.x,m.y,m.z)}else for(let x=0,M=t.count;x<M;x+=3)o.fromBufferAttribute(t,x+0),l.fromBufferAttribute(t,x+1),d.fromBufferAttribute(t,x+2),_.subVectors(d,l),S.subVectors(o,l),_.cross(S),r.setXYZ(x+0,_.x,_.y,_.z),r.setXYZ(x+1,_.x,_.y,_.z),r.setXYZ(x+2,_.x,_.y,_.z);this.normalizeNormals(),r.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,r=e.count;t<r;t++)vn.fromBufferAttribute(e,t),vn.normalize(),e.setXYZ(t,vn.x,vn.y,vn.z)}toNonIndexed(){function e(f,p){const m=f.array,_=f.itemSize,S=f.normalized,x=new m.constructor(p.length*_);let M=0,w=0;for(let A=0,v=p.length;A<v;A++){f.isInterleavedBufferAttribute?M=p[A]*f.data.stride+f.offset:M=p[A]*_;for(let y=0;y<_;y++)x[w++]=m[M++]}return new Ni(x,_,S)}if(this.index===null)return rt("BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Vn,r=this.index.array,o=this.attributes;for(const f in o){const p=o[f],m=e(p,r);t.setAttribute(f,m)}const l=this.morphAttributes;for(const f in l){const p=[],m=l[f];for(let _=0,S=m.length;_<S;_++){const x=m[_],M=e(x,r);p.push(M)}t.morphAttributes[f]=p}t.morphTargetsRelative=this.morphTargetsRelative;const d=this.groups;for(let f=0,p=d.length;f<p;f++){const m=d[f];t.addGroup(m.start,m.count,m.materialIndex)}return t}toJSON(){const e={metadata:{version:4.7,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.parameters!==void 0&&this._transformed===!0?"BufferGeometry":this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0&&this._transformed!==!0){const p=this.parameters;for(const m in p)p[m]!==void 0&&(e[m]=p[m]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const r=this.attributes;for(const p in r){const m=r[p];e.data.attributes[p]=m.toJSON(e.data)}const o={};let l=!1;for(const p in this.morphAttributes){const m=this.morphAttributes[p],_=[];for(let S=0,x=m.length;S<x;S++){const M=m[S];_.push(M.toJSON(e.data))}_.length>0&&(o[p]=_,l=!0)}l&&(e.data.morphAttributes=o,e.data.morphTargetsRelative=this.morphTargetsRelative);const d=this.groups;d.length>0&&(e.data.groups=JSON.parse(JSON.stringify(d)));const f=this.boundingSphere;return f!==null&&(e.data.boundingSphere=f.toJSON()),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const r=e.index;r!==null&&this.setIndex(r.clone());const o=e.attributes;for(const m in o){const _=o[m];this.setAttribute(m,_.clone(t))}const l=e.morphAttributes;for(const m in l){const _=[],S=l[m];for(let x=0,M=S.length;x<M;x++)_.push(S[x].clone(t));this.morphAttributes[m]=_}this.morphTargetsRelative=e.morphTargetsRelative;const d=e.groups;for(let m=0,_=d.length;m<_;m++){const S=d[m];this.addGroup(S.start,S.count,S.materialIndex)}const f=e.boundingBox;f!==null&&(this.boundingBox=f.clone());const p=e.boundingSphere;return p!==null&&(this.boundingSphere=p.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this._transformed=e._transformed,this}dispose(){this.dispatchEvent({type:"dispose"})}}let ZS=0;class wa extends ws{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:ZS++}),this.uuid=Ao(),this.name="",this.type="Material",this.blending=fa,this.side=Xr,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=sf,this.blendDst=af,this.blendEquation=vs,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ct(0,0,0),this.blendAlpha=0,this.depthFunc=ga,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=eg,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Zs,this.stencilZFail=Zs,this.stencilZPass=Zs,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const r=e[t];if(r===void 0){rt(`Material: parameter '${t}' has value of undefined.`);continue}const o=this[t];if(o===void 0){rt(`Material: '${t}' is not a property of THREE.${this.type}.`);continue}o&&o.isColor?o.set(r):o&&o.isVector2&&r&&r.isVector2||o&&o.isEuler&&r&&r.isEuler||o&&o.isVector3&&r&&r.isVector3?o.copy(r):this[t]=r}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const r={metadata:{version:4.7,type:"Material",generator:"Material.toJSON"}};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.color&&this.color.isColor&&(r.color=this.color.getHex()),this.roughness!==void 0&&(r.roughness=this.roughness),this.metalness!==void 0&&(r.metalness=this.metalness),this.sheen!==void 0&&(r.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(r.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(r.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(r.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(r.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(r.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(r.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(r.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(r.shininess=this.shininess),this.clearcoat!==void 0&&(r.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(r.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(r.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(r.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(r.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,r.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(r.sheenColorMap=this.sheenColorMap.toJSON(e).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(r.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(e).uuid),this.dispersion!==void 0&&(r.dispersion=this.dispersion),this.iridescence!==void 0&&(r.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(r.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(r.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(r.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(r.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(r.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(r.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(r.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(r.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(r.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(r.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(r.lightMap=this.lightMap.toJSON(e).uuid,r.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(r.aoMap=this.aoMap.toJSON(e).uuid,r.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(r.bumpMap=this.bumpMap.toJSON(e).uuid,r.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(r.normalMap=this.normalMap.toJSON(e).uuid,r.normalMapType=this.normalMapType,r.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(r.displacementMap=this.displacementMap.toJSON(e).uuid,r.displacementScale=this.displacementScale,r.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(r.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(r.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(r.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(r.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(r.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(r.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(r.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(r.combine=this.combine)),this.envMapRotation!==void 0&&(r.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(r.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(r.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(r.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(r.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(r.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(r.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(r.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(r.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(r.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(r.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(r.size=this.size),this.shadowSide!==null&&(r.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(r.sizeAttenuation=this.sizeAttenuation),this.blending!==fa&&(r.blending=this.blending),this.side!==Xr&&(r.side=this.side),this.vertexColors===!0&&(r.vertexColors=!0),this.opacity<1&&(r.opacity=this.opacity),this.transparent===!0&&(r.transparent=!0),this.blendSrc!==sf&&(r.blendSrc=this.blendSrc),this.blendDst!==af&&(r.blendDst=this.blendDst),this.blendEquation!==vs&&(r.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(r.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(r.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(r.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(r.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(r.blendAlpha=this.blendAlpha),this.depthFunc!==ga&&(r.depthFunc=this.depthFunc),this.depthTest===!1&&(r.depthTest=this.depthTest),this.depthWrite===!1&&(r.depthWrite=this.depthWrite),this.colorWrite===!1&&(r.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(r.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==eg&&(r.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(r.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(r.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Zs&&(r.stencilFail=this.stencilFail),this.stencilZFail!==Zs&&(r.stencilZFail=this.stencilZFail),this.stencilZPass!==Zs&&(r.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(r.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(r.rotation=this.rotation),this.polygonOffset===!0&&(r.polygonOffset=!0),this.polygonOffsetFactor!==0&&(r.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(r.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(r.linewidth=this.linewidth),this.dashSize!==void 0&&(r.dashSize=this.dashSize),this.gapSize!==void 0&&(r.gapSize=this.gapSize),this.scale!==void 0&&(r.scale=this.scale),this.dithering===!0&&(r.dithering=!0),this.alphaTest>0&&(r.alphaTest=this.alphaTest),this.alphaHash===!0&&(r.alphaHash=!0),this.alphaToCoverage===!0&&(r.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(r.premultipliedAlpha=!0),this.forceSinglePass===!0&&(r.forceSinglePass=!0),this.allowOverride===!1&&(r.allowOverride=!1),this.wireframe===!0&&(r.wireframe=!0),this.wireframeLinewidth>1&&(r.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(r.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(r.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(r.flatShading=!0),this.visible===!1&&(r.visible=!1),this.toneMapped===!1&&(r.toneMapped=!1),this.fog===!1&&(r.fog=!1),Object.keys(this.userData).length>0&&(r.userData=this.userData);function o(l){const d=[];for(const f in l){const p=l[f];delete p.metadata,d.push(p)}return d}if(t){const l=o(e.textures),d=o(e.images);l.length>0&&(r.textures=l),d.length>0&&(r.images=d)}return r}fromJSON(e,t){if(e.uuid!==void 0&&(this.uuid=e.uuid),e.name!==void 0&&(this.name=e.name),e.color!==void 0&&this.color!==void 0&&this.color.setHex(e.color),e.roughness!==void 0&&(this.roughness=e.roughness),e.metalness!==void 0&&(this.metalness=e.metalness),e.sheen!==void 0&&(this.sheen=e.sheen),e.sheenColor!==void 0&&(this.sheenColor=new Ct().setHex(e.sheenColor)),e.sheenRoughness!==void 0&&(this.sheenRoughness=e.sheenRoughness),e.emissive!==void 0&&this.emissive!==void 0&&this.emissive.setHex(e.emissive),e.specular!==void 0&&this.specular!==void 0&&this.specular.setHex(e.specular),e.specularIntensity!==void 0&&(this.specularIntensity=e.specularIntensity),e.specularColor!==void 0&&this.specularColor!==void 0&&this.specularColor.setHex(e.specularColor),e.shininess!==void 0&&(this.shininess=e.shininess),e.clearcoat!==void 0&&(this.clearcoat=e.clearcoat),e.clearcoatRoughness!==void 0&&(this.clearcoatRoughness=e.clearcoatRoughness),e.dispersion!==void 0&&(this.dispersion=e.dispersion),e.iridescence!==void 0&&(this.iridescence=e.iridescence),e.iridescenceIOR!==void 0&&(this.iridescenceIOR=e.iridescenceIOR),e.iridescenceThicknessRange!==void 0&&(this.iridescenceThicknessRange=e.iridescenceThicknessRange),e.transmission!==void 0&&(this.transmission=e.transmission),e.thickness!==void 0&&(this.thickness=e.thickness),e.attenuationDistance!==void 0&&(this.attenuationDistance=e.attenuationDistance),e.attenuationColor!==void 0&&this.attenuationColor!==void 0&&this.attenuationColor.setHex(e.attenuationColor),e.anisotropy!==void 0&&(this.anisotropy=e.anisotropy),e.anisotropyRotation!==void 0&&(this.anisotropyRotation=e.anisotropyRotation),e.fog!==void 0&&(this.fog=e.fog),e.flatShading!==void 0&&(this.flatShading=e.flatShading),e.blending!==void 0&&(this.blending=e.blending),e.combine!==void 0&&(this.combine=e.combine),e.side!==void 0&&(this.side=e.side),e.shadowSide!==void 0&&(this.shadowSide=e.shadowSide),e.opacity!==void 0&&(this.opacity=e.opacity),e.transparent!==void 0&&(this.transparent=e.transparent),e.alphaTest!==void 0&&(this.alphaTest=e.alphaTest),e.alphaHash!==void 0&&(this.alphaHash=e.alphaHash),e.depthFunc!==void 0&&(this.depthFunc=e.depthFunc),e.depthTest!==void 0&&(this.depthTest=e.depthTest),e.depthWrite!==void 0&&(this.depthWrite=e.depthWrite),e.colorWrite!==void 0&&(this.colorWrite=e.colorWrite),e.blendSrc!==void 0&&(this.blendSrc=e.blendSrc),e.blendDst!==void 0&&(this.blendDst=e.blendDst),e.blendEquation!==void 0&&(this.blendEquation=e.blendEquation),e.blendSrcAlpha!==void 0&&(this.blendSrcAlpha=e.blendSrcAlpha),e.blendDstAlpha!==void 0&&(this.blendDstAlpha=e.blendDstAlpha),e.blendEquationAlpha!==void 0&&(this.blendEquationAlpha=e.blendEquationAlpha),e.blendColor!==void 0&&this.blendColor!==void 0&&this.blendColor.setHex(e.blendColor),e.blendAlpha!==void 0&&(this.blendAlpha=e.blendAlpha),e.stencilWriteMask!==void 0&&(this.stencilWriteMask=e.stencilWriteMask),e.stencilFunc!==void 0&&(this.stencilFunc=e.stencilFunc),e.stencilRef!==void 0&&(this.stencilRef=e.stencilRef),e.stencilFuncMask!==void 0&&(this.stencilFuncMask=e.stencilFuncMask),e.stencilFail!==void 0&&(this.stencilFail=e.stencilFail),e.stencilZFail!==void 0&&(this.stencilZFail=e.stencilZFail),e.stencilZPass!==void 0&&(this.stencilZPass=e.stencilZPass),e.stencilWrite!==void 0&&(this.stencilWrite=e.stencilWrite),e.wireframe!==void 0&&(this.wireframe=e.wireframe),e.wireframeLinewidth!==void 0&&(this.wireframeLinewidth=e.wireframeLinewidth),e.wireframeLinecap!==void 0&&(this.wireframeLinecap=e.wireframeLinecap),e.wireframeLinejoin!==void 0&&(this.wireframeLinejoin=e.wireframeLinejoin),e.rotation!==void 0&&(this.rotation=e.rotation),e.linewidth!==void 0&&(this.linewidth=e.linewidth),e.dashSize!==void 0&&(this.dashSize=e.dashSize),e.gapSize!==void 0&&(this.gapSize=e.gapSize),e.scale!==void 0&&(this.scale=e.scale),e.polygonOffset!==void 0&&(this.polygonOffset=e.polygonOffset),e.polygonOffsetFactor!==void 0&&(this.polygonOffsetFactor=e.polygonOffsetFactor),e.polygonOffsetUnits!==void 0&&(this.polygonOffsetUnits=e.polygonOffsetUnits),e.dithering!==void 0&&(this.dithering=e.dithering),e.alphaToCoverage!==void 0&&(this.alphaToCoverage=e.alphaToCoverage),e.premultipliedAlpha!==void 0&&(this.premultipliedAlpha=e.premultipliedAlpha),e.forceSinglePass!==void 0&&(this.forceSinglePass=e.forceSinglePass),e.allowOverride!==void 0&&(this.allowOverride=e.allowOverride),e.visible!==void 0&&(this.visible=e.visible),e.toneMapped!==void 0&&(this.toneMapped=e.toneMapped),e.userData!==void 0&&(this.userData=e.userData),e.vertexColors!==void 0&&(typeof e.vertexColors=="number"?this.vertexColors=e.vertexColors>0:this.vertexColors=e.vertexColors),e.size!==void 0&&(this.size=e.size),e.sizeAttenuation!==void 0&&(this.sizeAttenuation=e.sizeAttenuation),e.map!==void 0&&(this.map=t[e.map]||null),e.matcap!==void 0&&(this.matcap=t[e.matcap]||null),e.alphaMap!==void 0&&(this.alphaMap=t[e.alphaMap]||null),e.bumpMap!==void 0&&(this.bumpMap=t[e.bumpMap]||null),e.bumpScale!==void 0&&(this.bumpScale=e.bumpScale),e.normalMap!==void 0&&(this.normalMap=t[e.normalMap]||null),e.normalMapType!==void 0&&(this.normalMapType=e.normalMapType),e.normalScale!==void 0){let r=e.normalScale;Array.isArray(r)===!1&&(r=[r,r]),this.normalScale=new yt().fromArray(r)}return e.displacementMap!==void 0&&(this.displacementMap=t[e.displacementMap]||null),e.displacementScale!==void 0&&(this.displacementScale=e.displacementScale),e.displacementBias!==void 0&&(this.displacementBias=e.displacementBias),e.roughnessMap!==void 0&&(this.roughnessMap=t[e.roughnessMap]||null),e.metalnessMap!==void 0&&(this.metalnessMap=t[e.metalnessMap]||null),e.emissiveMap!==void 0&&(this.emissiveMap=t[e.emissiveMap]||null),e.emissiveIntensity!==void 0&&(this.emissiveIntensity=e.emissiveIntensity),e.specularMap!==void 0&&(this.specularMap=t[e.specularMap]||null),e.specularIntensityMap!==void 0&&(this.specularIntensityMap=t[e.specularIntensityMap]||null),e.specularColorMap!==void 0&&(this.specularColorMap=t[e.specularColorMap]||null),e.envMap!==void 0&&(this.envMap=t[e.envMap]||null),e.envMapRotation!==void 0&&this.envMapRotation.fromArray(e.envMapRotation),e.envMapIntensity!==void 0&&(this.envMapIntensity=e.envMapIntensity),e.reflectivity!==void 0&&(this.reflectivity=e.reflectivity),e.refractionRatio!==void 0&&(this.refractionRatio=e.refractionRatio),e.lightMap!==void 0&&(this.lightMap=t[e.lightMap]||null),e.lightMapIntensity!==void 0&&(this.lightMapIntensity=e.lightMapIntensity),e.aoMap!==void 0&&(this.aoMap=t[e.aoMap]||null),e.aoMapIntensity!==void 0&&(this.aoMapIntensity=e.aoMapIntensity),e.gradientMap!==void 0&&(this.gradientMap=t[e.gradientMap]||null),e.clearcoatMap!==void 0&&(this.clearcoatMap=t[e.clearcoatMap]||null),e.clearcoatRoughnessMap!==void 0&&(this.clearcoatRoughnessMap=t[e.clearcoatRoughnessMap]||null),e.clearcoatNormalMap!==void 0&&(this.clearcoatNormalMap=t[e.clearcoatNormalMap]||null),e.clearcoatNormalScale!==void 0&&(this.clearcoatNormalScale=new yt().fromArray(e.clearcoatNormalScale)),e.iridescenceMap!==void 0&&(this.iridescenceMap=t[e.iridescenceMap]||null),e.iridescenceThicknessMap!==void 0&&(this.iridescenceThicknessMap=t[e.iridescenceThicknessMap]||null),e.transmissionMap!==void 0&&(this.transmissionMap=t[e.transmissionMap]||null),e.thicknessMap!==void 0&&(this.thicknessMap=t[e.thicknessMap]||null),e.anisotropyMap!==void 0&&(this.anisotropyMap=t[e.anisotropyMap]||null),e.sheenColorMap!==void 0&&(this.sheenColorMap=t[e.sheenColorMap]||null),e.sheenRoughnessMap!==void 0&&(this.sheenRoughnessMap=t[e.sheenRoughnessMap]||null),this}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let r=null;if(t!==null){const o=t.length;r=new Array(o);for(let l=0;l!==o;++l)r[l]=t[l].clone()}return this.clippingPlanes=r,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.allowOverride=e.allowOverride,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}}const rr=new Y,jd=new Y,Xl=new Y,Vr=new Y,Gd=new Y,ql=new Y,Wd=new Y;class fh{constructor(e=new Y,t=new Y(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,rr)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const r=t.dot(this.direction);return r<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,r)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=rr.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(rr.copy(this.origin).addScaledVector(this.direction,t),rr.distanceToSquared(e))}distanceSqToSegment(e,t,r,o){jd.copy(e).add(t).multiplyScalar(.5),Xl.copy(t).sub(e).normalize(),Vr.copy(this.origin).sub(jd);const l=e.distanceTo(t)*.5,d=-this.direction.dot(Xl),f=Vr.dot(this.direction),p=-Vr.dot(Xl),m=Vr.lengthSq(),_=Math.abs(1-d*d);let S,x,M,w;if(_>0)if(S=d*p-f,x=d*f-p,w=l*_,S>=0)if(x>=-w)if(x<=w){const A=1/_;S*=A,x*=A,M=S*(S+d*x+2*f)+x*(d*S+x+2*p)+m}else x=l,S=Math.max(0,-(d*x+f)),M=-S*S+x*(x+2*p)+m;else x=-l,S=Math.max(0,-(d*x+f)),M=-S*S+x*(x+2*p)+m;else x<=-w?(S=Math.max(0,-(-d*l+f)),x=S>0?-l:Math.min(Math.max(-l,-p),l),M=-S*S+x*(x+2*p)+m):x<=w?(S=0,x=Math.min(Math.max(-l,-p),l),M=x*(x+2*p)+m):(S=Math.max(0,-(d*l+f)),x=S>0?l:Math.min(Math.max(-l,-p),l),M=-S*S+x*(x+2*p)+m);else x=d>0?-l:l,S=Math.max(0,-(d*x+f)),M=-S*S+x*(x+2*p)+m;return r&&r.copy(this.origin).addScaledVector(this.direction,S),o&&o.copy(jd).addScaledVector(Xl,x),M}intersectSphere(e,t){rr.subVectors(e.center,this.origin);const r=rr.dot(this.direction),o=rr.dot(rr)-r*r,l=e.radius*e.radius;if(o>l)return null;const d=Math.sqrt(l-o),f=r-d,p=r+d;return p<0?null:f<0?this.at(p,t):this.at(f,t)}intersectsSphere(e){return e.radius<0?!1:this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const r=-(this.origin.dot(e.normal)+e.constant)/t;return r>=0?r:null}intersectPlane(e,t){const r=this.distanceToPlane(e);return r===null?null:this.at(r,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let r,o,l,d,f,p;const m=1/this.direction.x,_=1/this.direction.y,S=1/this.direction.z,x=this.origin;return m>=0?(r=(e.min.x-x.x)*m,o=(e.max.x-x.x)*m):(r=(e.max.x-x.x)*m,o=(e.min.x-x.x)*m),_>=0?(l=(e.min.y-x.y)*_,d=(e.max.y-x.y)*_):(l=(e.max.y-x.y)*_,d=(e.min.y-x.y)*_),r>d||l>o||((l>r||isNaN(r))&&(r=l),(d<o||isNaN(o))&&(o=d),S>=0?(f=(e.min.z-x.z)*S,p=(e.max.z-x.z)*S):(f=(e.max.z-x.z)*S,p=(e.min.z-x.z)*S),r>p||f>o)||((f>r||r!==r)&&(r=f),(p<o||o!==o)&&(o=p),o<0)?null:this.at(r>=0?r:o,t)}intersectsBox(e){return this.intersectBox(e,rr)!==null}intersectTriangle(e,t,r,o,l){Gd.subVectors(t,e),ql.subVectors(r,e),Wd.crossVectors(Gd,ql);let d=this.direction.dot(Wd),f;if(d>0){if(o)return null;f=1}else if(d<0)f=-1,d=-d;else return null;Vr.subVectors(this.origin,e);const p=f*this.direction.dot(ql.crossVectors(Vr,ql));if(p<0)return null;const m=f*this.direction.dot(Gd.cross(Vr));if(m<0||p+m>d)return null;const _=-f*Vr.dot(Wd);return _<0?null:this.at(_/d,l)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Eo extends wa{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Ct(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Es,this.combine=gx,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const gg=new en,ms=new fh,Yl=new No,xg=new Y,$l=new Y,Kl=new Y,Zl=new Y,Xd=new Y,Ql=new Y,vg=new Y,Jl=new Y;class mi extends Bn{constructor(e=new Vn,t=new Eo){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,r=Object.keys(t);if(r.length>0){const o=t[r[0]];if(o!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let l=0,d=o.length;l<d;l++){const f=o[l].name||String(l);this.morphTargetInfluences.push(0),this.morphTargetDictionary[f]=l}}}}getVertexPosition(e,t){const r=this.geometry,o=r.attributes.position,l=r.morphAttributes.position,d=r.morphTargetsRelative;t.fromBufferAttribute(o,e);const f=this.morphTargetInfluences;if(l&&f){Ql.set(0,0,0);for(let p=0,m=l.length;p<m;p++){const _=f[p],S=l[p];_!==0&&(Xd.fromBufferAttribute(S,e),d?Ql.addScaledVector(Xd,_):Ql.addScaledVector(Xd.sub(t),_))}t.add(Ql)}return t}raycast(e,t){const r=this.geometry,o=this.material,l=this.matrixWorld;o!==void 0&&(r.boundingSphere===null&&r.computeBoundingSphere(),Yl.copy(r.boundingSphere),Yl.applyMatrix4(l),ms.copy(e.ray).recast(e.near),!(Yl.containsPoint(ms.origin)===!1&&(ms.intersectSphere(Yl,xg)===null||ms.origin.distanceToSquared(xg)>(e.far-e.near)**2))&&(gg.copy(l).invert(),ms.copy(e.ray).applyMatrix4(gg),!(r.boundingBox!==null&&ms.intersectsBox(r.boundingBox)===!1)&&this._computeIntersections(e,t,ms)))}_computeIntersections(e,t,r){let o;const l=this.geometry,d=this.material,f=l.index,p=l.attributes.position,m=l.attributes.uv,_=l.attributes.uv1,S=l.attributes.normal,x=l.groups,M=l.drawRange;if(f!==null)if(Array.isArray(d))for(let w=0,A=x.length;w<A;w++){const v=x[w],y=d[v.materialIndex],P=Math.max(v.start,M.start),U=Math.min(f.count,Math.min(v.start+v.count,M.start+M.count));for(let N=P,L=U;N<L;N+=3){const R=f.getX(N),D=f.getX(N+1),E=f.getX(N+2);o=ec(this,y,e,r,m,_,S,R,D,E),o&&(o.faceIndex=Math.floor(N/3),o.face.materialIndex=v.materialIndex,t.push(o))}}else{const w=Math.max(0,M.start),A=Math.min(f.count,M.start+M.count);for(let v=w,y=A;v<y;v+=3){const P=f.getX(v),U=f.getX(v+1),N=f.getX(v+2);o=ec(this,d,e,r,m,_,S,P,U,N),o&&(o.faceIndex=Math.floor(v/3),t.push(o))}}else if(p!==void 0)if(Array.isArray(d))for(let w=0,A=x.length;w<A;w++){const v=x[w],y=d[v.materialIndex],P=Math.max(v.start,M.start),U=Math.min(p.count,Math.min(v.start+v.count,M.start+M.count));for(let N=P,L=U;N<L;N+=3){const R=N,D=N+1,E=N+2;o=ec(this,y,e,r,m,_,S,R,D,E),o&&(o.faceIndex=Math.floor(N/3),o.face.materialIndex=v.materialIndex,t.push(o))}}else{const w=Math.max(0,M.start),A=Math.min(p.count,M.start+M.count);for(let v=w,y=A;v<y;v+=3){const P=v,U=v+1,N=v+2;o=ec(this,d,e,r,m,_,S,P,U,N),o&&(o.faceIndex=Math.floor(v/3),t.push(o))}}}}function QS(s,e,t,r,o,l,d,f){let p;if(e.side===Zn?p=r.intersectTriangle(d,l,o,!0,f):p=r.intersectTriangle(o,l,d,e.side===Xr,f),p===null)return null;Jl.copy(f),Jl.applyMatrix4(s.matrixWorld);const m=t.ray.origin.distanceTo(Jl);return m<t.near||m>t.far?null:{distance:m,point:Jl.clone(),object:s}}function ec(s,e,t,r,o,l,d,f,p,m){s.getVertexPosition(f,$l),s.getVertexPosition(p,Kl),s.getVertexPosition(m,Zl);const _=QS(s,e,t,r,$l,Kl,Zl,vg);if(_){const S=new Y;Ai.getBarycoord(vg,$l,Kl,Zl,S),o&&(_.uv=Ai.getInterpolatedAttribute(o,f,p,m,S,new yt)),l&&(_.uv1=Ai.getInterpolatedAttribute(l,f,p,m,S,new yt)),d&&(_.normal=Ai.getInterpolatedAttribute(d,f,p,m,S,new Y),_.normal.dot(r.direction)>0&&_.normal.multiplyScalar(-1));const x={a:f,b:p,c:m,normal:new Y,materialIndex:0};Ai.getNormal($l,Kl,Zl,x.normal),_.face=x,_.barycoord=S}return _}class JS extends zn{constructor(e=null,t=1,r=1,o,l,d,f,p,m=wn,_=wn,S,x){super(null,d,f,p,m,_,o,l,S,x),this.isDataTexture=!0,this.image={data:e,width:t,height:r},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const qd=new Y,e1=new Y,t1=new ut;class xs{constructor(e=new Y(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,r,o){return this.normal.set(e,t,r),this.constant=o,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,r){const o=qd.subVectors(r,t).cross(e1.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(o,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t,r=!0){const o=e.delta(qd),l=this.normal.dot(o);if(l===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const d=-(e.start.dot(this.normal)+this.constant)/l;return r===!0&&(d<0||d>1)?null:t.copy(e.start).addScaledVector(o,d)}intersectsLine(e){const t=this.distanceToPoint(e.start),r=this.distanceToPoint(e.end);return t<0&&r>0||r<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const r=t||t1.getNormalMatrix(e),o=this.coplanarPoint(qd).applyMatrix4(e),l=this.normal.applyMatrix3(r).normalize();return this.constant=-o.dot(l),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const gs=new No,n1=new yt(.5,.5),tc=new Y;class Ox{constructor(e=new xs,t=new xs,r=new xs,o=new xs,l=new xs,d=new xs){this.planes=[e,t,r,o,l,d]}set(e,t,r,o,l,d){const f=this.planes;return f[0].copy(e),f[1].copy(t),f[2].copy(r),f[3].copy(o),f[4].copy(l),f[5].copy(d),this}copy(e){const t=this.planes;for(let r=0;r<6;r++)t[r].copy(e.planes[r]);return this}setFromProjectionMatrix(e,t=zi,r=!1){const o=this.planes,l=e.elements,d=l[0],f=l[1],p=l[2],m=l[3],_=l[4],S=l[5],x=l[6],M=l[7],w=l[8],A=l[9],v=l[10],y=l[11],P=l[12],U=l[13],N=l[14],L=l[15];if(o[0].setComponents(m-d,M-_,y-w,L-P).normalize(),o[1].setComponents(m+d,M+_,y+w,L+P).normalize(),o[2].setComponents(m+f,M+S,y+A,L+U).normalize(),o[3].setComponents(m-f,M-S,y-A,L-U).normalize(),r)o[4].setComponents(p,x,v,N).normalize(),o[5].setComponents(m-p,M-x,y-v,L-N).normalize();else if(o[4].setComponents(m-p,M-x,y-v,L-N).normalize(),t===zi)o[5].setComponents(m+p,M+x,y+v,L+N).normalize();else if(t===bc)o[5].setComponents(p,x,v,N).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),gs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),gs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(gs)}intersectsSprite(e){gs.center.set(0,0,0);const t=n1.distanceTo(e.center);return gs.radius=.7071067811865476+t,gs.applyMatrix4(e.matrixWorld),this.intersectsSphere(gs)}intersectsSphere(e){const t=this.planes,r=e.center,o=-e.radius;for(let l=0;l<6;l++)if(t[l].distanceToPoint(r)<o)return!1;return!0}intersectsBox(e){const t=this.planes;for(let r=0;r<6;r++){const o=t[r];if(tc.x=o.normal.x>0?e.max.x:e.min.x,tc.y=o.normal.y>0?e.max.y:e.min.y,tc.z=o.normal.z>0?e.max.z:e.min.z,o.distanceToPoint(tc)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let r=0;r<6;r++)if(t[r].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class zx extends wa{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new Ct(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const wc=new Y,Tc=new Y,_g=new en,vo=new fh,nc=new No,Yd=new Y,yg=new Y;class i1 extends Bn{constructor(e=new Vn,t=new zx){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,r=[0];for(let o=1,l=t.count;o<l;o++)wc.fromBufferAttribute(t,o-1),Tc.fromBufferAttribute(t,o),r[o]=r[o-1],r[o]+=wc.distanceTo(Tc);e.setAttribute("lineDistance",new Dn(r,1))}else rt("Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const r=this.geometry,o=this.matrixWorld,l=e.params.Line.threshold,d=r.drawRange;if(r.boundingSphere===null&&r.computeBoundingSphere(),nc.copy(r.boundingSphere),nc.applyMatrix4(o),nc.radius+=l,e.ray.intersectsSphere(nc)===!1)return;_g.copy(o).invert(),vo.copy(e.ray).applyMatrix4(_g);const f=l/((this.scale.x+this.scale.y+this.scale.z)/3),p=f*f,m=this.isLineSegments?2:1,_=r.index,x=r.attributes.position;if(_!==null){const M=Math.max(0,d.start),w=Math.min(_.count,d.start+d.count);for(let A=M,v=w-1;A<v;A+=m){const y=_.getX(A),P=_.getX(A+1),U=ic(this,e,vo,p,y,P,A);U&&t.push(U)}if(this.isLineLoop){const A=_.getX(w-1),v=_.getX(M),y=ic(this,e,vo,p,A,v,w-1);y&&t.push(y)}}else{const M=Math.max(0,d.start),w=Math.min(x.count,d.start+d.count);for(let A=M,v=w-1;A<v;A+=m){const y=ic(this,e,vo,p,A,A+1,A);y&&t.push(y)}if(this.isLineLoop){const A=ic(this,e,vo,p,w-1,M,w-1);A&&t.push(A)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,r=Object.keys(t);if(r.length>0){const o=t[r[0]];if(o!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let l=0,d=o.length;l<d;l++){const f=o[l].name||String(l);this.morphTargetInfluences.push(0),this.morphTargetDictionary[f]=l}}}}}function ic(s,e,t,r,o,l,d){const f=s.geometry.attributes.position;if(wc.fromBufferAttribute(f,o),Tc.fromBufferAttribute(f,l),t.distanceSqToSegment(wc,Tc,Yd,yg)>r)return;Yd.applyMatrix4(s.matrixWorld);const m=e.ray.origin.distanceTo(Yd);if(!(m<e.near||m>e.far))return{distance:m,point:yg.clone().applyMatrix4(s.matrixWorld),index:d,face:null,faceIndex:null,barycoord:null,object:s}}class r1 extends i1{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Bx extends wa{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new Ct(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Sg=new en,qf=new fh,rc=new No,sc=new Y;class s1 extends Bn{constructor(e=new Vn,t=new Bx){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const r=this.geometry,o=this.matrixWorld,l=e.params.Points.threshold,d=r.drawRange;if(r.boundingSphere===null&&r.computeBoundingSphere(),rc.copy(r.boundingSphere),rc.applyMatrix4(o),rc.radius+=l,e.ray.intersectsSphere(rc)===!1)return;Sg.copy(o).invert(),qf.copy(e.ray).applyMatrix4(Sg);const f=l/((this.scale.x+this.scale.y+this.scale.z)/3),p=f*f,m=r.index,S=r.attributes.position;if(m!==null){const x=Math.max(0,d.start),M=Math.min(m.count,d.start+d.count);for(let w=x,A=M;w<A;w++){const v=m.getX(w);sc.fromBufferAttribute(S,v),Mg(sc,v,p,o,e,t,this)}}else{const x=Math.max(0,d.start),M=Math.min(S.count,d.start+d.count);for(let w=x,A=M;w<A;w++)sc.fromBufferAttribute(S,w),Mg(sc,w,p,o,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,r=Object.keys(t);if(r.length>0){const o=t[r[0]];if(o!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let l=0,d=o.length;l<d;l++){const f=o[l].name||String(l);this.morphTargetInfluences.push(0),this.morphTargetDictionary[f]=l}}}}}function Mg(s,e,t,r,o,l,d){const f=qf.distanceSqToPoint(s);if(f<t){const p=new Y;qf.closestPointToPoint(s,p),p.applyMatrix4(r);const m=o.ray.origin.distanceTo(p);if(m<o.near||m>o.far)return;l.push({distance:m,distanceToRay:Math.sqrt(f),point:p,index:e,face:null,faceIndex:null,barycoord:null,object:d})}}class Vx extends zn{constructor(e=[],t=Ms,r,o,l,d,f,p,m,_){super(e,t,r,o,l,d,f,p,m,_),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class va extends zn{constructor(e,t,r=Hi,o,l,d,f=wn,p=wn,m,_=dr,S=1){if(_!==dr&&_!==Ss)throw new Error("THREE.DepthTexture: format must be either THREE.DepthFormat or THREE.DepthStencilFormat");const x={width:e,height:t,depth:S};super(x,o,l,d,f,p,_,r,m),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.source=new dh(Object.assign({},e.image)),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}class a1 extends va{constructor(e,t=Hi,r=Ms,o,l,d=wn,f=wn,p,m=dr){const _={width:e,height:e,depth:1},S=[_,_,_,_,_,_];super(e,e,t,r,o,l,d,f,p,m),this.image=S,this.isCubeDepthTexture=!0,this.isCubeTexture=!0}get images(){return this.image}set images(e){this.image=e}}class Hx extends zn{constructor(e=null){super(),this.sourceTexture=e,this.isExternalTexture=!0}copy(e){return super.copy(e),this.sourceTexture=e.sourceTexture,this}}class Ro extends Vn{constructor(e=1,t=1,r=1,o=1,l=1,d=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:r,widthSegments:o,heightSegments:l,depthSegments:d};const f=this;o=Math.floor(o),l=Math.floor(l),d=Math.floor(d);const p=[],m=[],_=[],S=[];let x=0,M=0;w("z","y","x",-1,-1,r,t,e,d,l,0),w("z","y","x",1,-1,r,t,-e,d,l,1),w("x","z","y",1,1,e,r,t,o,d,2),w("x","z","y",1,-1,e,r,-t,o,d,3),w("x","y","z",1,-1,e,t,r,o,l,4),w("x","y","z",-1,-1,e,t,-r,o,l,5),this.setIndex(p),this.setAttribute("position",new Dn(m,3)),this.setAttribute("normal",new Dn(_,3)),this.setAttribute("uv",new Dn(S,2));function w(A,v,y,P,U,N,L,R,D,E,I){const z=N/D,B=L/E,H=N/2,ce=L/2,he=R/2,Z=D+1,ue=E+1;let K=0,q=0;const se=new Y;for(let le=0;le<ue;le++){const k=le*B-ce;for(let Q=0;Q<Z;Q++){const Ue=Q*z-H;se[A]=Ue*P,se[v]=k*U,se[y]=he,m.push(se.x,se.y,se.z),se[A]=0,se[v]=0,se[y]=R>0?1:-1,_.push(se.x,se.y,se.z),S.push(Q/D),S.push(1-le/E),K+=1}}for(let le=0;le<E;le++)for(let k=0;k<D;k++){const Q=x+k+Z*le,Ue=x+k+Z*(le+1),$e=x+(k+1)+Z*(le+1),Ve=x+(k+1)+Z*le;p.push(Q,Ue,Ve),p.push(Ue,$e,Ve),q+=6}f.addGroup(M,q,I),M+=q,x+=K}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ro(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}class hh extends Vn{constructor(e=[],t=[],r=1,o=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:r,detail:o};const l=[],d=[];f(o),m(r),_(),this.setAttribute("position",new Dn(l,3)),this.setAttribute("normal",new Dn(l.slice(),3)),this.setAttribute("uv",new Dn(d,2)),o===0?this.computeVertexNormals():this.normalizeNormals();function f(P){const U=new Y,N=new Y,L=new Y;for(let R=0;R<t.length;R+=3)M(t[R+0],U),M(t[R+1],N),M(t[R+2],L),p(U,N,L,P)}function p(P,U,N,L){const R=L+1,D=[];for(let E=0;E<=R;E++){D[E]=[];const I=P.clone().lerp(N,E/R),z=U.clone().lerp(N,E/R),B=R-E;for(let H=0;H<=B;H++)H===0&&E===R?D[E][H]=I:D[E][H]=I.clone().lerp(z,H/B)}for(let E=0;E<R;E++)for(let I=0;I<2*(R-E)-1;I++){const z=Math.floor(I/2);I%2===0?(x(D[E][z+1]),x(D[E+1][z]),x(D[E][z])):(x(D[E][z+1]),x(D[E+1][z+1]),x(D[E+1][z]))}}function m(P){const U=new Y;for(let N=0;N<l.length;N+=3)U.x=l[N+0],U.y=l[N+1],U.z=l[N+2],U.normalize().multiplyScalar(P),l[N+0]=U.x,l[N+1]=U.y,l[N+2]=U.z}function _(){const P=new Y;for(let U=0;U<l.length;U+=3){P.x=l[U+0],P.y=l[U+1],P.z=l[U+2];const N=v(P)/2/Math.PI+.5,L=y(P)/Math.PI+.5;d.push(N,1-L)}w(),S()}function S(){for(let P=0;P<d.length;P+=6){const U=d[P+0],N=d[P+2],L=d[P+4],R=Math.max(U,N,L),D=Math.min(U,N,L);R>.9&&D<.1&&(U<.2&&(d[P+0]+=1),N<.2&&(d[P+2]+=1),L<.2&&(d[P+4]+=1))}}function x(P){l.push(P.x,P.y,P.z)}function M(P,U){const N=P*3;U.x=e[N+0],U.y=e[N+1],U.z=e[N+2]}function w(){const P=new Y,U=new Y,N=new Y,L=new Y,R=new yt,D=new yt,E=new yt;for(let I=0,z=0;I<l.length;I+=9,z+=6){P.set(l[I+0],l[I+1],l[I+2]),U.set(l[I+3],l[I+4],l[I+5]),N.set(l[I+6],l[I+7],l[I+8]),R.set(d[z+0],d[z+1]),D.set(d[z+2],d[z+3]),E.set(d[z+4],d[z+5]),L.copy(P).add(U).add(N).divideScalar(3);const B=v(L);A(R,z+0,P,B),A(D,z+2,U,B),A(E,z+4,N,B)}}function A(P,U,N,L){L<0&&P.x===1&&(d[U]=P.x-1),N.x===0&&N.z===0&&(d[U]=L/2/Math.PI+.5)}function v(P){return Math.atan2(P.z,-P.x)}function y(P){return Math.atan2(-P.y,Math.sqrt(P.x*P.x+P.z*P.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new hh(e.vertices,e.indices,e.radius,e.detail)}}class o1{constructor(){this.type="Curve",this.arcLengthDivisions=200,this.needsUpdate=!1,this.cacheArcLengths=null}getPoint(){rt("Curve: .getPoint() not implemented.")}getPointAt(e,t){const r=this.getUtoTmapping(e);return this.getPoint(r,t)}getPoints(e=5){const t=[];for(let r=0;r<=e;r++)t.push(this.getPoint(r/e));return t}getSpacedPoints(e=5){const t=[];for(let r=0;r<=e;r++)t.push(this.getPointAt(r/e));return t}getLength(){const e=this.getLengths();return e[e.length-1]}getLengths(e=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===e+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const t=[];let r,o=this.getPoint(0),l=0;t.push(0);for(let d=1;d<=e;d++)r=this.getPoint(d/e),l+=r.distanceTo(o),t.push(l),o=r;return this.cacheArcLengths=t,t}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(e,t=null){const r=this.getLengths();let o=0;const l=r.length;let d;t?d=t:d=e*r[l-1];let f=0,p=l-1,m;for(;f<=p;)if(o=Math.floor(f+(p-f)/2),m=r[o]-d,m<0)f=o+1;else if(m>0)p=o-1;else{p=o;break}if(o=p,r[o]===d)return o/(l-1);const _=r[o],x=r[o+1]-_,M=(d-_)/x;return(o+M)/(l-1)}getTangent(e,t){let o=e-1e-4,l=e+1e-4;o<0&&(o=0),l>1&&(l=1);const d=this.getPoint(o),f=this.getPoint(l),p=t||(d.isVector2?new yt:new Y);return p.copy(f).sub(d).normalize(),p}getTangentAt(e,t){const r=this.getUtoTmapping(e);return this.getTangent(r,t)}computeFrenetFrames(e,t=!1){const r=new Y,o=[],l=[],d=[],f=new Y,p=new en;for(let M=0;M<=e;M++){const w=M/e;o[M]=this.getTangentAt(w,new Y)}l[0]=new Y,d[0]=new Y;let m=Number.MAX_VALUE;const _=Math.abs(o[0].x),S=Math.abs(o[0].y),x=Math.abs(o[0].z);_<=m&&(m=_,r.set(1,0,0)),S<=m&&(m=S,r.set(0,1,0)),x<=m&&r.set(0,0,1),f.crossVectors(o[0],r).normalize(),l[0].crossVectors(o[0],f),d[0].crossVectors(o[0],l[0]);for(let M=1;M<=e;M++){if(l[M]=l[M-1].clone(),d[M]=d[M-1].clone(),f.crossVectors(o[M-1],o[M]),f.length()>Number.EPSILON){f.normalize();const w=Math.acos(vt(o[M-1].dot(o[M]),-1,1));l[M].applyMatrix4(p.makeRotationAxis(f,w))}d[M].crossVectors(o[M],l[M])}if(t===!0){let M=Math.acos(vt(l[0].dot(l[e]),-1,1));M/=e,o[0].dot(f.crossVectors(l[0],l[e]))>0&&(M=-M);for(let w=1;w<=e;w++)l[w].applyMatrix4(p.makeRotationAxis(o[w],M*w)),d[w].crossVectors(o[w],l[w])}return{tangents:o,normals:l,binormals:d}}clone(){return new this.constructor().copy(this)}copy(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}toJSON(){const e={metadata:{version:4.7,type:"Curve",generator:"Curve.toJSON"}};return e.arcLengthDivisions=this.arcLengthDivisions,e.type=this.type,e}fromJSON(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}}class l1 extends o1{constructor(e=0,t=0,r=1,o=1,l=0,d=Math.PI*2,f=!1,p=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=e,this.aY=t,this.xRadius=r,this.yRadius=o,this.aStartAngle=l,this.aEndAngle=d,this.aClockwise=f,this.aRotation=p}getPoint(e,t=new yt){const r=t,o=Math.PI*2;let l=this.aEndAngle-this.aStartAngle;const d=Math.abs(l)<Number.EPSILON;for(;l<0;)l+=o;for(;l>o;)l-=o;l<Number.EPSILON&&(d?l=0:l=o),this.aClockwise===!0&&!d&&(l===o?l=-o:l=l-o);const f=this.aStartAngle+e*l;let p=this.aX+this.xRadius*Math.cos(f),m=this.aY+this.yRadius*Math.sin(f);if(this.aRotation!==0){const _=Math.cos(this.aRotation),S=Math.sin(this.aRotation),x=p-this.aX,M=m-this.aY;p=x*_-M*S+this.aX,m=x*S+M*_+this.aY}return r.set(p,m)}copy(e){return super.copy(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}toJSON(){const e=super.toJSON();return e.aX=this.aX,e.aY=this.aY,e.xRadius=this.xRadius,e.yRadius=this.yRadius,e.aStartAngle=this.aStartAngle,e.aEndAngle=this.aEndAngle,e.aClockwise=this.aClockwise,e.aRotation=this.aRotation,e}fromJSON(e){return super.fromJSON(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}}class Ac extends hh{constructor(e=1,t=0){const r=(1+Math.sqrt(5))/2,o=[-1,r,0,1,r,0,-1,-r,0,1,-r,0,0,-1,r,0,1,r,0,-1,-r,0,1,-r,r,0,-1,r,0,1,-r,0,-1,-r,0,1],l=[0,11,5,0,5,1,0,1,7,0,7,10,0,10,11,1,5,9,5,11,4,11,10,2,10,7,6,7,1,8,3,9,4,3,4,2,3,2,6,3,6,8,3,8,9,4,9,5,2,4,11,6,2,10,8,6,7,9,8,1];super(o,l,e,t),this.type="IcosahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Ac(e.radius,e.detail)}}class Ic extends Vn{constructor(e=1,t=1,r=1,o=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:r,heightSegments:o};const l=e/2,d=t/2,f=Math.floor(r),p=Math.floor(o),m=f+1,_=p+1,S=e/f,x=t/p,M=[],w=[],A=[],v=[];for(let y=0;y<_;y++){const P=y*x-d;for(let U=0;U<m;U++){const N=U*S-l;w.push(N,-P,0),A.push(0,0,1),v.push(U/f),v.push(1-y/p)}}for(let y=0;y<p;y++)for(let P=0;P<f;P++){const U=P+m*y,N=P+m*(y+1),L=P+1+m*(y+1),R=P+1+m*y;M.push(U,N,R),M.push(N,L,R)}this.setIndex(M),this.setAttribute("position",new Dn(w,3)),this.setAttribute("normal",new Dn(A,3)),this.setAttribute("uv",new Dn(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ic(e.width,e.height,e.widthSegments,e.heightSegments)}}class ph extends Vn{constructor(e=1,t=32,r=16,o=0,l=Math.PI*2,d=0,f=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:r,phiStart:o,phiLength:l,thetaStart:d,thetaLength:f},t=Math.max(3,Math.floor(t)),r=Math.max(2,Math.floor(r));const p=Math.min(d+f,Math.PI);let m=0;const _=[],S=new Y,x=new Y,M=[],w=[],A=[],v=[];for(let y=0;y<=r;y++){const P=[],U=y/r,N=d+U*f,L=e*Math.cos(N),R=Math.sqrt(e*e-L*L);let D=0;y===0&&d===0?D=.5/t:y===r&&p===Math.PI&&(D=-.5/t);for(let E=0;E<=t;E++){const I=E/t,z=o+I*l;S.x=-R*Math.cos(z),S.y=L,S.z=R*Math.sin(z),w.push(S.x,S.y,S.z),x.copy(S).normalize(),A.push(x.x,x.y,x.z),v.push(I+D,1-U),P.push(m++)}_.push(P)}for(let y=0;y<r;y++)for(let P=0;P<t;P++){const U=_[y][P+1],N=_[y][P],L=_[y+1][P],R=_[y+1][P+1];(y!==0||d>0)&&M.push(U,N,R),(y!==r-1||p<Math.PI)&&M.push(N,L,R)}this.setIndex(M),this.setAttribute("position",new Dn(w,3)),this.setAttribute("normal",new Dn(A,3)),this.setAttribute("uv",new Dn(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ph(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}function _a(s){const e={};for(const t in s){e[t]={};for(const r in s[t]){const o=s[t][r];if(bg(o))o.isRenderTargetTexture?(rt("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][r]=null):e[t][r]=o.clone();else if(Array.isArray(o))if(bg(o[0])){const l=[];for(let d=0,f=o.length;d<f;d++)l[d]=o[d].clone();e[t][r]=l}else e[t][r]=o.slice();else e[t][r]=o}}return e}function On(s){const e={};for(let t=0;t<s.length;t++){const r=_a(s[t]);for(const o in r)e[o]=r[o]}return e}function bg(s){return s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)}function c1(s){const e=[];for(let t=0;t<s.length;t++)e.push(s[t].clone());return e}function jx(s){const e=s.getRenderTarget();return e===null?s.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:St.workingColorSpace}const u1={clone:_a,merge:On};var d1=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,f1=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class ji extends wa{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=d1,this.fragmentShader=f1,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=_a(e.uniforms),this.uniformsGroups=c1(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this.defaultAttributeValues=Object.assign({},e.defaultAttributeValues),this.index0AttributeName=e.index0AttributeName,this.uniformsNeedUpdate=e.uniformsNeedUpdate,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const o in this.uniforms){const d=this.uniforms[o].value;d&&d.isTexture?t.uniforms[o]={type:"t",value:d.toJSON(e).uuid}:d&&d.isColor?t.uniforms[o]={type:"c",value:d.getHex()}:d&&d.isVector2?t.uniforms[o]={type:"v2",value:d.toArray()}:d&&d.isVector3?t.uniforms[o]={type:"v3",value:d.toArray()}:d&&d.isVector4?t.uniforms[o]={type:"v4",value:d.toArray()}:d&&d.isMatrix3?t.uniforms[o]={type:"m3",value:d.toArray()}:d&&d.isMatrix4?t.uniforms[o]={type:"m4",value:d.toArray()}:t.uniforms[o]={value:d}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const r={};for(const o in this.extensions)this.extensions[o]===!0&&(r[o]=!0);return Object.keys(r).length>0&&(t.extensions=r),t}fromJSON(e,t){if(super.fromJSON(e,t),e.uniforms!==void 0)for(const r in e.uniforms){const o=e.uniforms[r];switch(this.uniforms[r]={},o.type){case"t":this.uniforms[r].value=t[o.value]||null;break;case"c":this.uniforms[r].value=new Ct().setHex(o.value);break;case"v2":this.uniforms[r].value=new yt().fromArray(o.value);break;case"v3":this.uniforms[r].value=new Y().fromArray(o.value);break;case"v4":this.uniforms[r].value=new sn().fromArray(o.value);break;case"m3":this.uniforms[r].value=new ut().fromArray(o.value);break;case"m4":this.uniforms[r].value=new en().fromArray(o.value);break;default:this.uniforms[r].value=o.value}}if(e.defines!==void 0&&(this.defines=e.defines),e.vertexShader!==void 0&&(this.vertexShader=e.vertexShader),e.fragmentShader!==void 0&&(this.fragmentShader=e.fragmentShader),e.glslVersion!==void 0&&(this.glslVersion=e.glslVersion),e.extensions!==void 0)for(const r in e.extensions)this.extensions[r]=e.extensions[r];return e.lights!==void 0&&(this.lights=e.lights),e.clipping!==void 0&&(this.clipping=e.clipping),this}}class h1 extends ji{constructor(e){super(e),this.isRawShaderMaterial=!0,this.type="RawShaderMaterial"}}class p1 extends wa{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=SS,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class m1 extends wa{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const ac=new Y,oc=new Ea,Ui=new Y;class Gx extends Bn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new en,this.projectionMatrix=new en,this.projectionMatrixInverse=new en,this.coordinateSystem=zi,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorld.decompose(ac,oc,Ui),Ui.x===1&&Ui.y===1&&Ui.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(ac,oc,Ui.set(1,1,1)).invert()}updateWorldMatrix(e,t,r=!1){super.updateWorldMatrix(e,t,r),this.matrixWorld.decompose(ac,oc,Ui),Ui.x===1&&Ui.y===1&&Ui.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(ac,oc,Ui.set(1,1,1)).invert()}clone(){return new this.constructor().copy(this)}}const Hr=new Y,Eg=new yt,wg=new yt;class hi extends Gx{constructor(e=50,t=1,r=.1,o=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=r,this.far=o,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Xf*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Ed*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Xf*2*Math.atan(Math.tan(Ed*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,r){Hr.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Hr.x,Hr.y).multiplyScalar(-e/Hr.z),Hr.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),r.set(Hr.x,Hr.y).multiplyScalar(-e/Hr.z)}getViewSize(e,t){return this.getViewBounds(e,Eg,wg),t.subVectors(wg,Eg)}setViewOffset(e,t,r,o,l,d){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=r,this.view.offsetY=o,this.view.width=l,this.view.height=d,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Ed*.5*this.fov)/this.zoom,r=2*t,o=this.aspect*r,l=-.5*o;const d=this.view;if(this.view!==null&&this.view.enabled){const p=d.fullWidth,m=d.fullHeight;l+=d.offsetX*o/p,t-=d.offsetY*r/m,o*=d.width/p,r*=d.height/m}const f=this.filmOffset;f!==0&&(l+=e*f/this.getFilmWidth()),this.projectionMatrix.makePerspective(l,l+o,t,t-r,e,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}class Wx extends Gx{constructor(e=-1,t=1,r=1,o=-1,l=.1,d=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=r,this.bottom=o,this.near=l,this.far=d,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,r,o,l,d){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=r,this.view.offsetY=o,this.view.width=l,this.view.height=d,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),r=(this.right+this.left)/2,o=(this.top+this.bottom)/2;let l=r-e,d=r+e,f=o+t,p=o-t;if(this.view!==null&&this.view.enabled){const m=(this.right-this.left)/this.view.fullWidth/this.zoom,_=(this.top-this.bottom)/this.view.fullHeight/this.zoom;l+=m*this.view.offsetX,d=l+m*this.view.width,f-=_*this.view.offsetY,p=f-_*this.view.height}this.projectionMatrix.makeOrthographic(l,d,f,p,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const la=-90,ca=1;class g1 extends Bn{constructor(e,t,r){super(),this.type="CubeCamera",this.renderTarget=r,this.coordinateSystem=null,this.activeMipmapLevel=0;const o=new hi(la,ca,e,t);o.layers=this.layers,this.add(o);const l=new hi(la,ca,e,t);l.layers=this.layers,this.add(l);const d=new hi(la,ca,e,t);d.layers=this.layers,this.add(d);const f=new hi(la,ca,e,t);f.layers=this.layers,this.add(f);const p=new hi(la,ca,e,t);p.layers=this.layers,this.add(p);const m=new hi(la,ca,e,t);m.layers=this.layers,this.add(m)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[r,o,l,d,f,p]=t;for(const m of t)this.remove(m);if(e===zi)r.up.set(0,1,0),r.lookAt(1,0,0),o.up.set(0,1,0),o.lookAt(-1,0,0),l.up.set(0,0,-1),l.lookAt(0,1,0),d.up.set(0,0,1),d.lookAt(0,-1,0),f.up.set(0,1,0),f.lookAt(0,0,1),p.up.set(0,1,0),p.lookAt(0,0,-1);else if(e===bc)r.up.set(0,-1,0),r.lookAt(-1,0,0),o.up.set(0,-1,0),o.lookAt(1,0,0),l.up.set(0,0,1),l.lookAt(0,1,0),d.up.set(0,0,-1),d.lookAt(0,-1,0),f.up.set(0,-1,0),f.lookAt(0,0,1),p.up.set(0,-1,0),p.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const m of t)this.add(m),m.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:r,activeMipmapLevel:o}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[l,d,f,p,m,_]=this.children,S=e.getRenderTarget(),x=e.getActiveCubeFace(),M=e.getActiveMipmapLevel(),w=e.xr.enabled;e.xr.enabled=!1;const A=r.texture.generateMipmaps;r.texture.generateMipmaps=!1;let v=!1;e.isWebGLRenderer===!0?v=e.state.buffers.depth.getReversed():v=e.reversedDepthBuffer,e.setRenderTarget(r,0,o),v&&e.autoClear===!1&&e.clearDepth(),e.render(t,l),e.setRenderTarget(r,1,o),v&&e.autoClear===!1&&e.clearDepth(),e.render(t,d),e.setRenderTarget(r,2,o),v&&e.autoClear===!1&&e.clearDepth(),e.render(t,f),e.setRenderTarget(r,3,o),v&&e.autoClear===!1&&e.clearDepth(),e.render(t,p),e.setRenderTarget(r,4,o),v&&e.autoClear===!1&&e.clearDepth(),e.render(t,m),r.texture.generateMipmaps=A,e.setRenderTarget(r,5,o),v&&e.autoClear===!1&&e.clearDepth(),e.render(t,_),e.setRenderTarget(S,x,M),e.xr.enabled=w,r.texture.needsPMREMUpdate=!0}}class x1 extends hi{constructor(e=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=e}}class v1{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1,rt("Clock: This module has been deprecated. Please use THREE.Timer instead.")}start(){this.startTime=performance.now(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=performance.now();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}const _h=class _h{constructor(e,t,r,o){this.elements=[1,0,0,1],e!==void 0&&this.set(e,t,r,o)}identity(){return this.set(1,0,0,1),this}fromArray(e,t=0){for(let r=0;r<4;r++)this.elements[r]=e[r+t];return this}set(e,t,r,o){const l=this.elements;return l[0]=e,l[2]=t,l[1]=r,l[3]=o,this}};_h.prototype.isMatrix2=!0;let Tg=_h;function Ag(s,e,t,r){const o=_1(r);switch(t){case Nx:return s*e;case Px:return s*e/o.components*o.byteLength;case ah:return s*e/o.components*o.byteLength;case bs:return s*e*2/o.components*o.byteLength;case oh:return s*e*2/o.components*o.byteLength;case Rx:return s*e*3/o.components*o.byteLength;case Ci:return s*e*4/o.components*o.byteLength;case lh:return s*e*4/o.components*o.byteLength;case dc:case fc:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*8;case hc:case pc:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*16;case xf:case _f:return Math.max(s,16)*Math.max(e,8)/4;case gf:case vf:return Math.max(s,8)*Math.max(e,8)/2;case yf:case Sf:case bf:case Ef:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*8;case Mf:case _c:case wf:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*16;case Tf:return Math.floor((s+3)/4)*Math.floor((e+3)/4)*16;case Af:return Math.floor((s+4)/5)*Math.floor((e+3)/4)*16;case Cf:return Math.floor((s+4)/5)*Math.floor((e+4)/5)*16;case Nf:return Math.floor((s+5)/6)*Math.floor((e+4)/5)*16;case Rf:return Math.floor((s+5)/6)*Math.floor((e+5)/6)*16;case Pf:return Math.floor((s+7)/8)*Math.floor((e+4)/5)*16;case Lf:return Math.floor((s+7)/8)*Math.floor((e+5)/6)*16;case If:return Math.floor((s+7)/8)*Math.floor((e+7)/8)*16;case Df:return Math.floor((s+9)/10)*Math.floor((e+4)/5)*16;case Uf:return Math.floor((s+9)/10)*Math.floor((e+5)/6)*16;case Ff:return Math.floor((s+9)/10)*Math.floor((e+7)/8)*16;case kf:return Math.floor((s+9)/10)*Math.floor((e+9)/10)*16;case Of:return Math.floor((s+11)/12)*Math.floor((e+9)/10)*16;case zf:return Math.floor((s+11)/12)*Math.floor((e+11)/12)*16;case Bf:case Vf:case Hf:return Math.ceil(s/4)*Math.ceil(e/4)*16;case jf:case Gf:return Math.ceil(s/4)*Math.ceil(e/4)*8;case yc:case Wf:return Math.ceil(s/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function _1(s){switch(s){case pi:case wx:return{byteLength:1,components:1};case wo:case Tx:case ur:return{byteLength:2,components:1};case rh:case sh:return{byteLength:2,components:4};case Hi:case ih:case Oi:return{byteLength:4,components:1};case Ax:case Cx:return{byteLength:4,components:3}}throw new Error(`THREE.TextureUtils: Unknown texture type ${s}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:nh}}));typeof window<"u"&&(window.__THREE__?rt("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=nh);/**
 * @license
 * Copyright 2010-2026 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function Xx(){let s=null,e=!1,t=null,r=null;function o(l,d){t(l,d),r=s.requestAnimationFrame(o)}return{start:function(){e!==!0&&t!==null&&s!==null&&(r=s.requestAnimationFrame(o),e=!0)},stop:function(){s!==null&&s.cancelAnimationFrame(r),e=!1},setAnimationLoop:function(l){t=l},setContext:function(l){s=l}}}function y1(s){const e=new WeakMap;function t(f,p){const m=f.array,_=f.usage,S=m.byteLength,x=s.createBuffer();s.bindBuffer(p,x),s.bufferData(p,m,_),f.onUploadCallback();let M;if(m instanceof Float32Array)M=s.FLOAT;else if(typeof Float16Array<"u"&&m instanceof Float16Array)M=s.HALF_FLOAT;else if(m instanceof Uint16Array)f.isFloat16BufferAttribute?M=s.HALF_FLOAT:M=s.UNSIGNED_SHORT;else if(m instanceof Int16Array)M=s.SHORT;else if(m instanceof Uint32Array)M=s.UNSIGNED_INT;else if(m instanceof Int32Array)M=s.INT;else if(m instanceof Int8Array)M=s.BYTE;else if(m instanceof Uint8Array)M=s.UNSIGNED_BYTE;else if(m instanceof Uint8ClampedArray)M=s.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+m);return{buffer:x,type:M,bytesPerElement:m.BYTES_PER_ELEMENT,version:f.version,size:S}}function r(f,p,m){const _=p.array,S=p.updateRanges;if(s.bindBuffer(m,f),S.length===0)s.bufferSubData(m,0,_);else{S.sort((M,w)=>M.start-w.start);let x=0;for(let M=1;M<S.length;M++){const w=S[x],A=S[M];A.start<=w.start+w.count+1?w.count=Math.max(w.count,A.start+A.count-w.start):(++x,S[x]=A)}S.length=x+1;for(let M=0,w=S.length;M<w;M++){const A=S[M];s.bufferSubData(m,A.start*_.BYTES_PER_ELEMENT,_,A.start,A.count)}p.clearUpdateRanges()}p.onUploadCallback()}function o(f){return f.isInterleavedBufferAttribute&&(f=f.data),e.get(f)}function l(f){f.isInterleavedBufferAttribute&&(f=f.data);const p=e.get(f);p&&(s.deleteBuffer(p.buffer),e.delete(f))}function d(f,p){if(f.isInterleavedBufferAttribute&&(f=f.data),f.isGLBufferAttribute){const _=e.get(f);(!_||_.version<f.version)&&e.set(f,{buffer:f.buffer,type:f.type,bytesPerElement:f.elementSize,version:f.version});return}const m=e.get(f);if(m===void 0)e.set(f,t(f,p));else if(m.version<f.version){if(m.size!==f.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");r(m.buffer,f,p),m.version=f.version}}return{get:o,remove:l,update:d}}var S1=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,M1=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,b1=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,E1=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,w1=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,T1=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,A1=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,C1=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,N1=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec4 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 );
	}
#endif`,R1=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,P1=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,L1=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,I1=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,D1=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,U1=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,F1=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,k1=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,O1=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,z1=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,B1=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#endif`,V1=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#endif`,H1=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec4 vColor;
#endif`,j1=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec4( 1.0 );
#endif
#ifdef USE_COLOR_ALPHA
	vColor *= color;
#elif defined( USE_COLOR )
	vColor.rgb *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.rgb *= instanceColor.rgb;
#endif
#ifdef USE_BATCHING_COLOR
	vColor *= getBatchingColor( getIndirectIndex( gl_DrawID ) );
#endif`,G1=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
#define inverseTransformDirection transformDirectionByInverseViewMatrix
vec3 transformNormalByInverseViewMatrix( in vec3 normal, in mat4 viewMatrix ) {
	return normalize( ( vec4( normal, 0.0 ) * viewMatrix ).xyz );
}
vec3 transformDirectionByInverseViewMatrix( in vec3 dir, in mat4 viewMatrix ) {
	return normalize( ( vec4( dir, 0.0 ) * viewMatrix ).xyz );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,W1=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,X1=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
#endif`,q1=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Y1=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,$1=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,K1=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Z1="gl_FragColor = linearToOutputTexel( gl_FragColor );",Q1=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,J1=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * reflectVec );
		#ifdef ENVMAP_BLENDING_MULTIPLY
			outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_MIX )
			outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_ADD )
			outgoingLight += envColor.xyz * specularStrength * reflectivity;
		#endif
	#endif
#endif`,eM=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
#endif`,tM=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,nM=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,iM=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,rM=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,sM=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,aM=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,oM=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,lM=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,cM=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,uM=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,dM=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,fM=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif
#include <lightprobes_pars_fragment>`,hM=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, pow4( roughness ) ) );
			reflectVec = transformDirectionByInverseViewMatrix( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,pM=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,mM=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,gM=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,xM=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,vM=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.diffuseContribution = diffuseColor.rgb * ( 1.0 - metalnessFactor );
material.metalness = metalnessFactor;
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor;
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = vec3( 0.04 );
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.0001, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,_M=`uniform sampler2D dfgLUT;
struct PhysicalMaterial {
	vec3 diffuseColor;
	vec3 diffuseContribution;
	vec3 specularColor;
	vec3 specularColorBlended;
	float roughness;
	float metalness;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
		vec3 iridescenceFresnelDielectric;
		vec3 iridescenceFresnelMetallic;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		return 0.5 / max( gv + gl, EPSILON );
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColorBlended;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transpose( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float rInv = 1.0 / ( roughness + 0.1 );
	float a = -1.9362 + 1.0678 * roughness + 0.4573 * r2 - 0.8469 * rInv;
	float b = -0.6014 + 0.5538 * roughness - 0.4670 * r2 - 0.1255 * rInv;
	float DG = exp( a * dotNV + b );
	return saturate( DG );
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
vec3 BRDF_GGX_Multiscatter( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 singleScatter = BRDF_GGX( lightDir, viewDir, normal, material );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 dfgV = texture2D( dfgLUT, vec2( material.roughness, dotNV ) ).rg;
	vec2 dfgL = texture2D( dfgLUT, vec2( material.roughness, dotNL ) ).rg;
	vec3 FssEss_V = material.specularColorBlended * dfgV.x + material.specularF90 * dfgV.y;
	vec3 FssEss_L = material.specularColorBlended * dfgL.x + material.specularF90 * dfgL.y;
	float Ess_V = dfgV.x + dfgV.y;
	float Ess_L = dfgL.x + dfgL.y;
	float Ems_V = 1.0 - Ess_V;
	float Ems_L = 1.0 - Ess_L;
	vec3 Favg = material.specularColorBlended + ( 1.0 - material.specularColorBlended ) * 0.047619;
	vec3 Fms = FssEss_V * FssEss_L * Favg / ( 1.0 - Ems_V * Ems_L * Favg + EPSILON );
	float compensationFactor = Ems_V * Ems_L;
	vec3 multiScatter = Fms * compensationFactor;
	return singleScatter + multiScatter;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColorBlended * t2.x + ( material.specularF90 - material.specularColorBlended ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseContribution * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
		#ifdef USE_CLEARCOAT
			vec3 Ncc = geometryClearcoatNormal;
			vec2 uvClearcoat = LTC_Uv( Ncc, viewDir, material.clearcoatRoughness );
			vec4 t1Clearcoat = texture2D( ltc_1, uvClearcoat );
			vec4 t2Clearcoat = texture2D( ltc_2, uvClearcoat );
			mat3 mInvClearcoat = mat3(
				vec3( t1Clearcoat.x, 0, t1Clearcoat.y ),
				vec3(             0, 1,             0 ),
				vec3( t1Clearcoat.z, 0, t1Clearcoat.w )
			);
			vec3 fresnelClearcoat = material.clearcoatF0 * t2Clearcoat.x + ( material.clearcoatF90 - material.clearcoatF0 ) * t2Clearcoat.y;
			clearcoatSpecularDirect += lightColor * fresnelClearcoat * LTC_Evaluate( Ncc, viewDir, position, mInvClearcoat, rectCoords );
		#endif
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
 
 		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
 
 		float sheenAlbedoV = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
 		float sheenAlbedoL = IBLSheenBRDF( geometryNormal, directLight.direction, material.sheenRoughness );
 
 		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * max( sheenAlbedoV, sheenAlbedoL );
 
 		irradiance *= sheenEnergyComp;
 
 	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX_Multiscatter( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 diffuse = irradiance * BRDF_Lambert( material.diffuseContribution );
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		diffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectDiffuse += diffuse;
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness ) * RECIPROCAL_PI;
 	#endif
	vec3 singleScatteringDielectric = vec3( 0.0 );
	vec3 multiScatteringDielectric = vec3( 0.0 );
	vec3 singleScatteringMetallic = vec3( 0.0 );
	vec3 multiScatteringMetallic = vec3( 0.0 );
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnelDielectric, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.iridescence, material.iridescenceFresnelMetallic, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscattering( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#endif
	vec3 singleScattering = mix( singleScatteringDielectric, singleScatteringMetallic, material.metalness );
	vec3 multiScattering = mix( multiScatteringDielectric, multiScatteringMetallic, material.metalness );
	vec3 totalScatteringDielectric = singleScatteringDielectric + multiScatteringDielectric;
	vec3 diffuse = material.diffuseContribution * ( 1.0 - totalScatteringDielectric );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	vec3 indirectSpecular = radiance * singleScattering;
	indirectSpecular += multiScattering * cosineWeightedIrradiance;
	vec3 indirectDiffuse = diffuse * cosineWeightedIrradiance;
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		indirectSpecular *= sheenEnergyComp;
		indirectDiffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectSpecular += indirectSpecular;
	reflectedLight.indirectDiffuse += indirectDiffuse;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,yM=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnelDielectric = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceFresnelMetallic = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.diffuseColor );
		material.iridescenceFresnel = mix( material.iridescenceFresnelDielectric, material.iridescenceFresnelMetallic, material.metalness );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS ) && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
	#ifdef USE_LIGHT_PROBES_GRID
		vec3 probeWorldPos = ( ( vec4( geometryPosition, 1.0 ) - viewMatrix[ 3 ] ) * viewMatrix ).xyz;
		vec3 probeWorldNormal = transformNormalByInverseViewMatrix( geometryNormal, viewMatrix );
		irradiance += getLightProbeGridIrradiance( probeWorldPos, probeWorldNormal );
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,SM=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
		#if defined( STANDARD ) || defined( LAMBERT ) || defined( PHONG )
			iblIrradiance += getIBLIrradiance( geometryNormal );
		#endif
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,MM=`#if defined( RE_IndirectDiffuse )
	#if defined( LAMBERT ) || defined( PHONG )
		irradiance += iblIrradiance;
	#endif
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,bM=`#ifdef USE_LIGHT_PROBES_GRID
uniform highp sampler3D probesSH;
uniform vec3 probesMin;
uniform vec3 probesMax;
uniform vec3 probesResolution;
vec3 getLightProbeGridIrradiance( vec3 worldPos, vec3 worldNormal ) {
	vec3 res = probesResolution;
	vec3 gridRange = probesMax - probesMin;
	vec3 resMinusOne = res - 1.0;
	vec3 probeSpacing = gridRange / resMinusOne;
	vec3 samplePos = worldPos + worldNormal * probeSpacing * 0.5;
	vec3 uvw = clamp( ( samplePos - probesMin ) / gridRange, 0.0, 1.0 );
	uvw = uvw * resMinusOne / res + 0.5 / res;
	float nz          = res.z;
	float paddedSlices = nz + 2.0;
	float atlasDepth  = 7.0 * paddedSlices;
	float uvZBase     = uvw.z * nz + 1.0;
	vec4 s0 = texture( probesSH, vec3( uvw.xy, ( uvZBase                       ) / atlasDepth ) );
	vec4 s1 = texture( probesSH, vec3( uvw.xy, ( uvZBase +       paddedSlices   ) / atlasDepth ) );
	vec4 s2 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 2.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s3 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 3.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s4 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 4.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s5 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 5.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s6 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 6.0 * paddedSlices   ) / atlasDepth ) );
	vec3 c0 = s0.xyz;
	vec3 c1 = vec3( s0.w, s1.xy );
	vec3 c2 = vec3( s1.zw, s2.x );
	vec3 c3 = s2.yzw;
	vec3 c4 = s3.xyz;
	vec3 c5 = vec3( s3.w, s4.xy );
	vec3 c6 = vec3( s4.zw, s5.x );
	vec3 c7 = s5.yzw;
	vec3 c8 = s6.xyz;
	float x = worldNormal.x, y = worldNormal.y, z = worldNormal.z;
	vec3 result = c0 * 0.886227;
	result += c1 * 2.0 * 0.511664 * y;
	result += c2 * 2.0 * 0.511664 * z;
	result += c3 * 2.0 * 0.511664 * x;
	result += c4 * 2.0 * 0.429043 * x * y;
	result += c5 * 2.0 * 0.429043 * y * z;
	result += c6 * ( 0.743125 * z * z - 0.247708 );
	result += c7 * 2.0 * 0.429043 * x * z;
	result += c8 * 0.429043 * ( x * x - y * y );
	return max( result, vec3( 0.0 ) );
}
#endif`,EM=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,wM=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,TM=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,AM=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,CM=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,NM=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,RM=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,PM=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,LM=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,IM=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,DM=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,UM=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,FM=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,kM=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,OM=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,zM=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#ifdef DOUBLE_SIDED
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#ifdef DOUBLE_SIDED
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,BM=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#if defined( USE_PACKED_NORMALMAP )
		mapN = vec3( mapN.xy, sqrt( saturate( 1.0 - dot( mapN.xy, mapN.xy ) ) ) );
	#endif
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,VM=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,HM=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,jM=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
		#ifdef FLIP_SIDED
			vBitangent = - vBitangent;
		#endif
	#endif
#endif`,GM=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,WM=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,XM=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,qM=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,YM=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,$M=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,KM=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	#ifdef USE_REVERSED_DEPTH_BUFFER
	
		return depth * ( far - near ) - far;
	#else
		return depth * ( near - far ) - near;
	#endif
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	
	#ifdef USE_REVERSED_DEPTH_BUFFER
		return ( near * far ) / ( ( near - far ) * depth - near );
	#else
		return ( near * far ) / ( ( far - near ) * depth - far );
	#endif
}`,ZM=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,QM=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,JM=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,eb=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,tb=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,nb=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,ib=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#else
			uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#endif
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#else
			uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#endif
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform samplerCubeShadow pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#elif defined( SHADOWMAP_TYPE_BASIC )
			uniform samplerCube pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#endif
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float interleavedGradientNoise( vec2 position ) {
			return fract( 52.9829189 * fract( dot( position, vec2( 0.06711056, 0.00583715 ) ) ) );
		}
		vec2 vogelDiskSample( int sampleIndex, int samplesCount, float phi ) {
			const float goldenAngle = 2.399963229728653;
			float r = sqrt( ( float( sampleIndex ) + 0.5 ) / float( samplesCount ) );
			float theta = float( sampleIndex ) * goldenAngle + phi;
			return vec2( cos( theta ), sin( theta ) ) * r;
		}
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float getShadow( sampler2DShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			shadowCoord.z += shadowBias;
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
				float radius = shadowRadius * texelSize.x;
				float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
				shadow = (
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 0, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 1, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 2, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 3, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 4, 5, phi ) * radius, shadowCoord.z ) )
				) * 0.2;
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#elif defined( SHADOWMAP_TYPE_VSM )
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 distribution = texture2D( shadowMap, shadowCoord.xy ).rg;
				float mean = distribution.x;
				float variance = distribution.y * distribution.y;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					float hard_shadow = step( mean, shadowCoord.z );
				#else
					float hard_shadow = step( shadowCoord.z, mean );
				#endif
				
				if ( hard_shadow == 1.0 ) {
					shadow = 1.0;
				} else {
					variance = max( variance, 0.0000001 );
					float d = shadowCoord.z - mean;
					float p_max = variance / ( variance + d * d );
					p_max = clamp( ( p_max - 0.3 ) / 0.65, 0.0, 1.0 );
					shadow = max( hard_shadow, p_max );
				}
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#else
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				float depth = texture2D( shadowMap, shadowCoord.xy ).r;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					shadow = step( depth, shadowCoord.z );
				#else
					shadow = step( shadowCoord.z, depth );
				#endif
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	#if defined( SHADOWMAP_TYPE_PCF )
	float getPointShadow( samplerCubeShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 bd3D = normalize( lightToPosition );
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				float dp = ( shadowCameraNear * ( shadowCameraFar - viewSpaceZ ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp -= shadowBias;
			#else
				float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp += shadowBias;
			#endif
			float texelSize = shadowRadius / shadowMapSize.x;
			vec3 absDir = abs( bd3D );
			vec3 tangent = absDir.x > absDir.z ? vec3( 0.0, 1.0, 0.0 ) : vec3( 1.0, 0.0, 0.0 );
			tangent = normalize( cross( bd3D, tangent ) );
			vec3 bitangent = cross( bd3D, tangent );
			float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
			vec2 sample0 = vogelDiskSample( 0, 5, phi );
			vec2 sample1 = vogelDiskSample( 1, 5, phi );
			vec2 sample2 = vogelDiskSample( 2, 5, phi );
			vec2 sample3 = vogelDiskSample( 3, 5, phi );
			vec2 sample4 = vogelDiskSample( 4, 5, phi );
			shadow = (
				texture( shadowMap, vec4( bd3D + ( tangent * sample0.x + bitangent * sample0.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample1.x + bitangent * sample1.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample2.x + bitangent * sample2.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample3.x + bitangent * sample3.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample4.x + bitangent * sample4.y ) * texelSize, dp ) )
			) * 0.2;
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#elif defined( SHADOWMAP_TYPE_BASIC )
	float getPointShadow( samplerCube shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			float depth = textureCube( shadowMap, bd3D ).r;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				depth = 1.0 - depth;
			#endif
			shadow = step( dp, depth );
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#endif
	#endif
#endif`,rb=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,sb=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	#ifdef HAS_NORMAL
		vec3 shadowWorldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
	#else
		vec3 shadowWorldNormal = vec3( 0.0 );
	#endif
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,ab=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0 && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,ob=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,lb=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,cb=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,ub=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,db=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,fb=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,hb=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,pb=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,mb=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseContribution, material.specularColorBlended, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,gb=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,xb=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,vb=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,_b=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,yb=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const Sb=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,Mb=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,bb=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Eb=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vWorldDirection );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,wb=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Tb=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ab=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,Cb=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,Nb=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,Rb=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = vec4( dist, 0.0, 0.0, 1.0 );
}`,Pb=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Lb=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ib=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,Db=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Ub=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,Fb=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,kb=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Ob=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,zb=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,Bb=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Vb=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,Hb=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( normalize( normal ) * 0.5 + 0.5, diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,jb=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Gb=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Wb=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,Xb=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
 
		outgoingLight = outgoingLight + sheenSpecularDirect + sheenSpecularIndirect;
 
 	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,qb=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Yb=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,$b=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,Kb=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Zb=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Qb=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Jb=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,eE=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,pt={alphahash_fragment:S1,alphahash_pars_fragment:M1,alphamap_fragment:b1,alphamap_pars_fragment:E1,alphatest_fragment:w1,alphatest_pars_fragment:T1,aomap_fragment:A1,aomap_pars_fragment:C1,batching_pars_vertex:N1,batching_vertex:R1,begin_vertex:P1,beginnormal_vertex:L1,bsdfs:I1,iridescence_fragment:D1,bumpmap_pars_fragment:U1,clipping_planes_fragment:F1,clipping_planes_pars_fragment:k1,clipping_planes_pars_vertex:O1,clipping_planes_vertex:z1,color_fragment:B1,color_pars_fragment:V1,color_pars_vertex:H1,color_vertex:j1,common:G1,cube_uv_reflection_fragment:W1,defaultnormal_vertex:X1,displacementmap_pars_vertex:q1,displacementmap_vertex:Y1,emissivemap_fragment:$1,emissivemap_pars_fragment:K1,colorspace_fragment:Z1,colorspace_pars_fragment:Q1,envmap_fragment:J1,envmap_common_pars_fragment:eM,envmap_pars_fragment:tM,envmap_pars_vertex:nM,envmap_physical_pars_fragment:hM,envmap_vertex:iM,fog_vertex:rM,fog_pars_vertex:sM,fog_fragment:aM,fog_pars_fragment:oM,gradientmap_pars_fragment:lM,lightmap_pars_fragment:cM,lights_lambert_fragment:uM,lights_lambert_pars_fragment:dM,lights_pars_begin:fM,lights_toon_fragment:pM,lights_toon_pars_fragment:mM,lights_phong_fragment:gM,lights_phong_pars_fragment:xM,lights_physical_fragment:vM,lights_physical_pars_fragment:_M,lights_fragment_begin:yM,lights_fragment_maps:SM,lights_fragment_end:MM,lightprobes_pars_fragment:bM,logdepthbuf_fragment:EM,logdepthbuf_pars_fragment:wM,logdepthbuf_pars_vertex:TM,logdepthbuf_vertex:AM,map_fragment:CM,map_pars_fragment:NM,map_particle_fragment:RM,map_particle_pars_fragment:PM,metalnessmap_fragment:LM,metalnessmap_pars_fragment:IM,morphinstance_vertex:DM,morphcolor_vertex:UM,morphnormal_vertex:FM,morphtarget_pars_vertex:kM,morphtarget_vertex:OM,normal_fragment_begin:zM,normal_fragment_maps:BM,normal_pars_fragment:VM,normal_pars_vertex:HM,normal_vertex:jM,normalmap_pars_fragment:GM,clearcoat_normal_fragment_begin:WM,clearcoat_normal_fragment_maps:XM,clearcoat_pars_fragment:qM,iridescence_pars_fragment:YM,opaque_fragment:$M,packing:KM,premultiplied_alpha_fragment:ZM,project_vertex:QM,dithering_fragment:JM,dithering_pars_fragment:eb,roughnessmap_fragment:tb,roughnessmap_pars_fragment:nb,shadowmap_pars_fragment:ib,shadowmap_pars_vertex:rb,shadowmap_vertex:sb,shadowmask_pars_fragment:ab,skinbase_vertex:ob,skinning_pars_vertex:lb,skinning_vertex:cb,skinnormal_vertex:ub,specularmap_fragment:db,specularmap_pars_fragment:fb,tonemapping_fragment:hb,tonemapping_pars_fragment:pb,transmission_fragment:mb,transmission_pars_fragment:gb,uv_pars_fragment:xb,uv_pars_vertex:vb,uv_vertex:_b,worldpos_vertex:yb,background_vert:Sb,background_frag:Mb,backgroundCube_vert:bb,backgroundCube_frag:Eb,cube_vert:wb,cube_frag:Tb,depth_vert:Ab,depth_frag:Cb,distance_vert:Nb,distance_frag:Rb,equirect_vert:Pb,equirect_frag:Lb,linedashed_vert:Ib,linedashed_frag:Db,meshbasic_vert:Ub,meshbasic_frag:Fb,meshlambert_vert:kb,meshlambert_frag:Ob,meshmatcap_vert:zb,meshmatcap_frag:Bb,meshnormal_vert:Vb,meshnormal_frag:Hb,meshphong_vert:jb,meshphong_frag:Gb,meshphysical_vert:Wb,meshphysical_frag:Xb,meshtoon_vert:qb,meshtoon_frag:Yb,points_vert:$b,points_frag:Kb,shadow_vert:Zb,shadow_frag:Qb,sprite_vert:Jb,sprite_frag:eE},De={common:{diffuse:{value:new Ct(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ut},alphaMap:{value:null},alphaMapTransform:{value:new ut},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ut}},envmap:{envMap:{value:null},envMapRotation:{value:new ut},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98},dfgLUT:{value:null}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ut}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ut}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ut},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ut},normalScale:{value:new yt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ut},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ut}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ut}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ut}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ct(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null},probesSH:{value:null},probesMin:{value:new Y},probesMax:{value:new Y},probesResolution:{value:new Y}},points:{diffuse:{value:new Ct(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ut},alphaTest:{value:0},uvTransform:{value:new ut}},sprite:{diffuse:{value:new Ct(16777215)},opacity:{value:1},center:{value:new yt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ut},alphaMap:{value:null},alphaMapTransform:{value:new ut},alphaTest:{value:0}}},ki={basic:{uniforms:On([De.common,De.specularmap,De.envmap,De.aomap,De.lightmap,De.fog]),vertexShader:pt.meshbasic_vert,fragmentShader:pt.meshbasic_frag},lambert:{uniforms:On([De.common,De.specularmap,De.envmap,De.aomap,De.lightmap,De.emissivemap,De.bumpmap,De.normalmap,De.displacementmap,De.fog,De.lights,{emissive:{value:new Ct(0)},envMapIntensity:{value:1}}]),vertexShader:pt.meshlambert_vert,fragmentShader:pt.meshlambert_frag},phong:{uniforms:On([De.common,De.specularmap,De.envmap,De.aomap,De.lightmap,De.emissivemap,De.bumpmap,De.normalmap,De.displacementmap,De.fog,De.lights,{emissive:{value:new Ct(0)},specular:{value:new Ct(1118481)},shininess:{value:30},envMapIntensity:{value:1}}]),vertexShader:pt.meshphong_vert,fragmentShader:pt.meshphong_frag},standard:{uniforms:On([De.common,De.envmap,De.aomap,De.lightmap,De.emissivemap,De.bumpmap,De.normalmap,De.displacementmap,De.roughnessmap,De.metalnessmap,De.fog,De.lights,{emissive:{value:new Ct(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:pt.meshphysical_vert,fragmentShader:pt.meshphysical_frag},toon:{uniforms:On([De.common,De.aomap,De.lightmap,De.emissivemap,De.bumpmap,De.normalmap,De.displacementmap,De.gradientmap,De.fog,De.lights,{emissive:{value:new Ct(0)}}]),vertexShader:pt.meshtoon_vert,fragmentShader:pt.meshtoon_frag},matcap:{uniforms:On([De.common,De.bumpmap,De.normalmap,De.displacementmap,De.fog,{matcap:{value:null}}]),vertexShader:pt.meshmatcap_vert,fragmentShader:pt.meshmatcap_frag},points:{uniforms:On([De.points,De.fog]),vertexShader:pt.points_vert,fragmentShader:pt.points_frag},dashed:{uniforms:On([De.common,De.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:pt.linedashed_vert,fragmentShader:pt.linedashed_frag},depth:{uniforms:On([De.common,De.displacementmap]),vertexShader:pt.depth_vert,fragmentShader:pt.depth_frag},normal:{uniforms:On([De.common,De.bumpmap,De.normalmap,De.displacementmap,{opacity:{value:1}}]),vertexShader:pt.meshnormal_vert,fragmentShader:pt.meshnormal_frag},sprite:{uniforms:On([De.sprite,De.fog]),vertexShader:pt.sprite_vert,fragmentShader:pt.sprite_frag},background:{uniforms:{uvTransform:{value:new ut},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:pt.background_vert,fragmentShader:pt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ut}},vertexShader:pt.backgroundCube_vert,fragmentShader:pt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:pt.cube_vert,fragmentShader:pt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:pt.equirect_vert,fragmentShader:pt.equirect_frag},distance:{uniforms:On([De.common,De.displacementmap,{referencePosition:{value:new Y},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:pt.distance_vert,fragmentShader:pt.distance_frag},shadow:{uniforms:On([De.lights,De.fog,{color:{value:new Ct(0)},opacity:{value:1}}]),vertexShader:pt.shadow_vert,fragmentShader:pt.shadow_frag}};ki.physical={uniforms:On([ki.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ut},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ut},clearcoatNormalScale:{value:new yt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ut},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ut},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ut},sheen:{value:0},sheenColor:{value:new Ct(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ut},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ut},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ut},transmissionSamplerSize:{value:new yt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ut},attenuationDistance:{value:0},attenuationColor:{value:new Ct(0)},specularColor:{value:new Ct(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ut},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ut},anisotropyVector:{value:new yt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ut}}]),vertexShader:pt.meshphysical_vert,fragmentShader:pt.meshphysical_frag};const lc={r:0,b:0,g:0},tE=new en,qx=new ut;qx.set(-1,0,0,0,1,0,0,0,1);function nE(s,e,t,r,o,l){const d=new Ct(0);let f=o===!0?0:1,p,m,_=null,S=0,x=null;function M(P){let U=P.isScene===!0?P.background:null;if(U&&U.isTexture){const N=P.backgroundBlurriness>0;U=e.get(U,N)}return U}function w(P){let U=!1;const N=M(P);N===null?v(d,f):N&&N.isColor&&(v(N,1),U=!0);const L=s.xr.getEnvironmentBlendMode();L==="additive"?t.buffers.color.setClear(0,0,0,1,l):L==="alpha-blend"&&t.buffers.color.setClear(0,0,0,0,l),(s.autoClear||U)&&(t.buffers.depth.setTest(!0),t.buffers.depth.setMask(!0),t.buffers.color.setMask(!0),s.clear(s.autoClearColor,s.autoClearDepth,s.autoClearStencil))}function A(P,U){const N=M(U);N&&(N.isCubeTexture||N.mapping===Lc)?(m===void 0&&(m=new mi(new Ro(1,1,1),new ji({name:"BackgroundCubeMaterial",uniforms:_a(ki.backgroundCube.uniforms),vertexShader:ki.backgroundCube.vertexShader,fragmentShader:ki.backgroundCube.fragmentShader,side:Zn,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),m.geometry.deleteAttribute("normal"),m.geometry.deleteAttribute("uv"),m.onBeforeRender=function(L,R,D){this.matrixWorld.copyPosition(D.matrixWorld)},Object.defineProperty(m.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(m)),m.material.uniforms.envMap.value=N,m.material.uniforms.backgroundBlurriness.value=U.backgroundBlurriness,m.material.uniforms.backgroundIntensity.value=U.backgroundIntensity,m.material.uniforms.backgroundRotation.value.setFromMatrix4(tE.makeRotationFromEuler(U.backgroundRotation)).transpose(),N.isCubeTexture&&N.isRenderTargetTexture===!1&&m.material.uniforms.backgroundRotation.value.premultiply(qx),m.material.toneMapped=St.getTransfer(N.colorSpace)!==Ft,(_!==N||S!==N.version||x!==s.toneMapping)&&(m.material.needsUpdate=!0,_=N,S=N.version,x=s.toneMapping),m.layers.enableAll(),P.unshift(m,m.geometry,m.material,0,0,null)):N&&N.isTexture&&(p===void 0&&(p=new mi(new Ic(2,2),new ji({name:"BackgroundMaterial",uniforms:_a(ki.background.uniforms),vertexShader:ki.background.vertexShader,fragmentShader:ki.background.fragmentShader,side:Xr,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),p.geometry.deleteAttribute("normal"),Object.defineProperty(p.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(p)),p.material.uniforms.t2D.value=N,p.material.uniforms.backgroundIntensity.value=U.backgroundIntensity,p.material.toneMapped=St.getTransfer(N.colorSpace)!==Ft,N.matrixAutoUpdate===!0&&N.updateMatrix(),p.material.uniforms.uvTransform.value.copy(N.matrix),(_!==N||S!==N.version||x!==s.toneMapping)&&(p.material.needsUpdate=!0,_=N,S=N.version,x=s.toneMapping),p.layers.enableAll(),P.unshift(p,p.geometry,p.material,0,0,null))}function v(P,U){P.getRGB(lc,jx(s)),t.buffers.color.setClear(lc.r,lc.g,lc.b,U,l)}function y(){m!==void 0&&(m.geometry.dispose(),m.material.dispose(),m=void 0),p!==void 0&&(p.geometry.dispose(),p.material.dispose(),p=void 0)}return{getClearColor:function(){return d},setClearColor:function(P,U=1){d.set(P),f=U,v(d,f)},getClearAlpha:function(){return f},setClearAlpha:function(P){f=P,v(d,f)},render:w,addToRenderList:A,dispose:y}}function iE(s,e){const t=s.getParameter(s.MAX_VERTEX_ATTRIBS),r={},o=x(null);let l=o,d=!1;function f(B,H,ce,he,Z){let ue=!1;const K=S(B,he,ce,H);l!==K&&(l=K,m(l.object)),ue=M(B,he,ce,Z),ue&&w(B,he,ce,Z),Z!==null&&e.update(Z,s.ELEMENT_ARRAY_BUFFER),(ue||d)&&(d=!1,N(B,H,ce,he),Z!==null&&s.bindBuffer(s.ELEMENT_ARRAY_BUFFER,e.get(Z).buffer))}function p(){return s.createVertexArray()}function m(B){return s.bindVertexArray(B)}function _(B){return s.deleteVertexArray(B)}function S(B,H,ce,he){const Z=he.wireframe===!0;let ue=r[H.id];ue===void 0&&(ue={},r[H.id]=ue);const K=B.isInstancedMesh===!0?B.id:0;let q=ue[K];q===void 0&&(q={},ue[K]=q);let se=q[ce.id];se===void 0&&(se={},q[ce.id]=se);let le=se[Z];return le===void 0&&(le=x(p()),se[Z]=le),le}function x(B){const H=[],ce=[],he=[];for(let Z=0;Z<t;Z++)H[Z]=0,ce[Z]=0,he[Z]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ce,attributeDivisors:he,object:B,attributes:{},index:null}}function M(B,H,ce,he){const Z=l.attributes,ue=H.attributes;let K=0;const q=ce.getAttributes();for(const se in q)if(q[se].location>=0){const k=Z[se];let Q=ue[se];if(Q===void 0&&(se==="instanceMatrix"&&B.instanceMatrix&&(Q=B.instanceMatrix),se==="instanceColor"&&B.instanceColor&&(Q=B.instanceColor)),k===void 0||k.attribute!==Q||Q&&k.data!==Q.data)return!0;K++}return l.attributesNum!==K||l.index!==he}function w(B,H,ce,he){const Z={},ue=H.attributes;let K=0;const q=ce.getAttributes();for(const se in q)if(q[se].location>=0){let k=ue[se];k===void 0&&(se==="instanceMatrix"&&B.instanceMatrix&&(k=B.instanceMatrix),se==="instanceColor"&&B.instanceColor&&(k=B.instanceColor));const Q={};Q.attribute=k,k&&k.data&&(Q.data=k.data),Z[se]=Q,K++}l.attributes=Z,l.attributesNum=K,l.index=he}function A(){const B=l.newAttributes;for(let H=0,ce=B.length;H<ce;H++)B[H]=0}function v(B){y(B,0)}function y(B,H){const ce=l.newAttributes,he=l.enabledAttributes,Z=l.attributeDivisors;ce[B]=1,he[B]===0&&(s.enableVertexAttribArray(B),he[B]=1),Z[B]!==H&&(s.vertexAttribDivisor(B,H),Z[B]=H)}function P(){const B=l.newAttributes,H=l.enabledAttributes;for(let ce=0,he=H.length;ce<he;ce++)H[ce]!==B[ce]&&(s.disableVertexAttribArray(ce),H[ce]=0)}function U(B,H,ce,he,Z,ue,K){K===!0?s.vertexAttribIPointer(B,H,ce,Z,ue):s.vertexAttribPointer(B,H,ce,he,Z,ue)}function N(B,H,ce,he){A();const Z=he.attributes,ue=ce.getAttributes(),K=H.defaultAttributeValues;for(const q in ue){const se=ue[q];if(se.location>=0){let le=Z[q];if(le===void 0&&(q==="instanceMatrix"&&B.instanceMatrix&&(le=B.instanceMatrix),q==="instanceColor"&&B.instanceColor&&(le=B.instanceColor)),le!==void 0){const k=le.normalized,Q=le.itemSize,Ue=e.get(le);if(Ue===void 0)continue;const $e=Ue.buffer,Ve=Ue.type,re=Ue.bytesPerElement,_e=Ve===s.INT||Ve===s.UNSIGNED_INT||le.gpuType===ih;if(le.isInterleavedBufferAttribute){const me=le.data,Fe=me.stride,Je=le.offset;if(me.isInstancedInterleavedBuffer){for(let et=0;et<se.locationSize;et++)y(se.location+et,me.meshPerAttribute);B.isInstancedMesh!==!0&&he._maxInstanceCount===void 0&&(he._maxInstanceCount=me.meshPerAttribute*me.count)}else for(let et=0;et<se.locationSize;et++)v(se.location+et);s.bindBuffer(s.ARRAY_BUFFER,$e);for(let et=0;et<se.locationSize;et++)U(se.location+et,Q/se.locationSize,Ve,k,Fe*re,(Je+Q/se.locationSize*et)*re,_e)}else{if(le.isInstancedBufferAttribute){for(let me=0;me<se.locationSize;me++)y(se.location+me,le.meshPerAttribute);B.isInstancedMesh!==!0&&he._maxInstanceCount===void 0&&(he._maxInstanceCount=le.meshPerAttribute*le.count)}else for(let me=0;me<se.locationSize;me++)v(se.location+me);s.bindBuffer(s.ARRAY_BUFFER,$e);for(let me=0;me<se.locationSize;me++)U(se.location+me,Q/se.locationSize,Ve,k,Q*re,Q/se.locationSize*me*re,_e)}}else if(K!==void 0){const k=K[q];if(k!==void 0)switch(k.length){case 2:s.vertexAttrib2fv(se.location,k);break;case 3:s.vertexAttrib3fv(se.location,k);break;case 4:s.vertexAttrib4fv(se.location,k);break;default:s.vertexAttrib1fv(se.location,k)}}}}P()}function L(){I();for(const B in r){const H=r[B];for(const ce in H){const he=H[ce];for(const Z in he){const ue=he[Z];for(const K in ue)_(ue[K].object),delete ue[K];delete he[Z]}}delete r[B]}}function R(B){if(r[B.id]===void 0)return;const H=r[B.id];for(const ce in H){const he=H[ce];for(const Z in he){const ue=he[Z];for(const K in ue)_(ue[K].object),delete ue[K];delete he[Z]}}delete r[B.id]}function D(B){for(const H in r){const ce=r[H];for(const he in ce){const Z=ce[he];if(Z[B.id]===void 0)continue;const ue=Z[B.id];for(const K in ue)_(ue[K].object),delete ue[K];delete Z[B.id]}}}function E(B){for(const H in r){const ce=r[H],he=B.isInstancedMesh===!0?B.id:0,Z=ce[he];if(Z!==void 0){for(const ue in Z){const K=Z[ue];for(const q in K)_(K[q].object),delete K[q];delete Z[ue]}delete ce[he],Object.keys(ce).length===0&&delete r[H]}}}function I(){z(),d=!0,l!==o&&(l=o,m(l.object))}function z(){o.geometry=null,o.program=null,o.wireframe=!1}return{setup:f,reset:I,resetDefaultState:z,dispose:L,releaseStatesOfGeometry:R,releaseStatesOfObject:E,releaseStatesOfProgram:D,initAttributes:A,enableAttribute:v,disableUnusedAttributes:P}}function rE(s,e,t){let r;function o(p){r=p}function l(p,m){s.drawArrays(r,p,m),t.update(m,r,1)}function d(p,m,_){_!==0&&(s.drawArraysInstanced(r,p,m,_),t.update(m,r,_))}function f(p,m,_){if(_===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(r,p,0,m,0,_);let x=0;for(let M=0;M<_;M++)x+=m[M];t.update(x,r,1)}this.setMode=o,this.render=l,this.renderInstances=d,this.renderMultiDraw=f}function sE(s,e,t,r){let o;function l(){if(o!==void 0)return o;if(e.has("EXT_texture_filter_anisotropic")===!0){const D=e.get("EXT_texture_filter_anisotropic");o=s.getParameter(D.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else o=0;return o}function d(D){return!(D!==Ci&&r.convert(D)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_FORMAT))}function f(D){const E=D===ur&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(D!==pi&&r.convert(D)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_TYPE)&&D!==Oi&&!E)}function p(D){if(D==="highp"){if(s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.HIGH_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.HIGH_FLOAT).precision>0)return"highp";D="mediump"}return D==="mediump"&&s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.MEDIUM_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let m=t.precision!==void 0?t.precision:"highp";const _=p(m);_!==m&&(rt("WebGLRenderer:",m,"not supported, using",_,"instead."),m=_);const S=t.logarithmicDepthBuffer===!0,x=t.reversedDepthBuffer===!0&&e.has("EXT_clip_control");t.reversedDepthBuffer===!0&&x===!1&&rt("WebGLRenderer: Unable to use reversed depth buffer due to missing EXT_clip_control extension. Fallback to default depth buffer.");const M=s.getParameter(s.MAX_TEXTURE_IMAGE_UNITS),w=s.getParameter(s.MAX_VERTEX_TEXTURE_IMAGE_UNITS),A=s.getParameter(s.MAX_TEXTURE_SIZE),v=s.getParameter(s.MAX_CUBE_MAP_TEXTURE_SIZE),y=s.getParameter(s.MAX_VERTEX_ATTRIBS),P=s.getParameter(s.MAX_VERTEX_UNIFORM_VECTORS),U=s.getParameter(s.MAX_VARYING_VECTORS),N=s.getParameter(s.MAX_FRAGMENT_UNIFORM_VECTORS),L=s.getParameter(s.MAX_SAMPLES),R=s.getParameter(s.SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:l,getMaxPrecision:p,textureFormatReadable:d,textureTypeReadable:f,precision:m,logarithmicDepthBuffer:S,reversedDepthBuffer:x,maxTextures:M,maxVertexTextures:w,maxTextureSize:A,maxCubemapSize:v,maxAttributes:y,maxVertexUniforms:P,maxVaryings:U,maxFragmentUniforms:N,maxSamples:L,samples:R}}function aE(s){const e=this;let t=null,r=0,o=!1,l=!1;const d=new xs,f=new ut,p={value:null,needsUpdate:!1};this.uniform=p,this.numPlanes=0,this.numIntersection=0,this.init=function(S,x){const M=S.length!==0||x||r!==0||o;return o=x,r=S.length,M},this.beginShadows=function(){l=!0,_(null)},this.endShadows=function(){l=!1},this.setGlobalState=function(S,x){t=_(S,x,0)},this.setState=function(S,x,M){const w=S.clippingPlanes,A=S.clipIntersection,v=S.clipShadows,y=s.get(S);if(!o||w===null||w.length===0||l&&!v)l?_(null):m();else{const P=l?0:r,U=P*4;let N=y.clippingState||null;p.value=N,N=_(w,x,U,M);for(let L=0;L!==U;++L)N[L]=t[L];y.clippingState=N,this.numIntersection=A?this.numPlanes:0,this.numPlanes+=P}};function m(){p.value!==t&&(p.value=t,p.needsUpdate=r>0),e.numPlanes=r,e.numIntersection=0}function _(S,x,M,w){const A=S!==null?S.length:0;let v=null;if(A!==0){if(v=p.value,w!==!0||v===null){const y=M+A*4,P=x.matrixWorldInverse;f.getNormalMatrix(P),(v===null||v.length<y)&&(v=new Float32Array(y));for(let U=0,N=M;U!==A;++U,N+=4)d.copy(S[U]).applyMatrix4(P,f),d.normal.toArray(v,N),v[N+3]=d.constant}p.value=v,p.needsUpdate=!0}return e.numPlanes=A,e.numIntersection=0,v}}const Gr=4,Cg=[.125,.215,.35,.446,.526,.582],_s=20,oE=256,_o=new Wx,Ng=new Ct;let $d=null,Kd=0,Zd=0,Qd=!1;const lE=new Y;class Rg{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._sizeLods=[],this._sigmas=[],this._lodMeshes=[],this._backgroundBox=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._blurMaterial=null,this._ggxMaterial=null}fromScene(e,t=0,r=.1,o=100,l={}){const{size:d=256,position:f=lE}=l;$d=this._renderer.getRenderTarget(),Kd=this._renderer.getActiveCubeFace(),Zd=this._renderer.getActiveMipmapLevel(),Qd=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(d);const p=this._allocateTargets();return p.depthBuffer=!0,this._sceneToCubeUV(e,r,o,p,f),t>0&&this._blur(p,0,0,t),this._applyPMREM(p),this._cleanup(p),p}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Ig(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Lg(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose(),this._backgroundBox!==null&&(this._backgroundBox.geometry.dispose(),this._backgroundBox.material.dispose())}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._ggxMaterial!==null&&this._ggxMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodMeshes.length;e++)this._lodMeshes[e].geometry.dispose()}_cleanup(e){this._renderer.setRenderTarget($d,Kd,Zd),this._renderer.xr.enabled=Qd,e.scissorTest=!1,ua(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Ms||e.mapping===xa?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),$d=this._renderer.getRenderTarget(),Kd=this._renderer.getActiveCubeFace(),Zd=this._renderer.getActiveMipmapLevel(),Qd=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const r=t||this._allocateTargets();return this._textureToCubeUV(e,r),this._applyPMREM(r),this._cleanup(r),r}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,r={magFilter:In,minFilter:In,generateMipmaps:!1,type:ur,format:Ci,colorSpace:Sc,depthBuffer:!1},o=Pg(e,t,r);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Pg(e,t,r);const{_lodMax:l}=this;({lodMeshes:this._lodMeshes,sizeLods:this._sizeLods,sigmas:this._sigmas}=cE(l)),this._blurMaterial=dE(l,e,t),this._ggxMaterial=uE(l,e,t)}return o}_compileMaterial(e){const t=new mi(new Vn,e);this._renderer.compile(t,_o)}_sceneToCubeUV(e,t,r,o,l){const p=new hi(90,1,t,r),m=[1,-1,1,1,1,1],_=[1,1,1,-1,-1,-1],S=this._renderer,x=S.autoClear,M=S.toneMapping;S.getClearColor(Ng),S.toneMapping=Bi,S.autoClear=!1,S.state.buffers.depth.getReversed()&&(S.setRenderTarget(o),S.clearDepth(),S.setRenderTarget(null)),this._backgroundBox===null&&(this._backgroundBox=new mi(new Ro,new Eo({name:"PMREM.Background",side:Zn,depthWrite:!1,depthTest:!1})));const A=this._backgroundBox,v=A.material;let y=!1;const P=e.background;P?P.isColor&&(v.color.copy(P),e.background=null,y=!0):(v.color.copy(Ng),y=!0);for(let U=0;U<6;U++){const N=U%3;N===0?(p.up.set(0,m[U],0),p.position.set(l.x,l.y,l.z),p.lookAt(l.x+_[U],l.y,l.z)):N===1?(p.up.set(0,0,m[U]),p.position.set(l.x,l.y,l.z),p.lookAt(l.x,l.y+_[U],l.z)):(p.up.set(0,m[U],0),p.position.set(l.x,l.y,l.z),p.lookAt(l.x,l.y,l.z+_[U]));const L=this._cubeSize;ua(o,N*L,U>2?L:0,L,L),S.setRenderTarget(o),y&&S.render(A,p),S.render(e,p)}S.toneMapping=M,S.autoClear=x,e.background=P}_textureToCubeUV(e,t){const r=this._renderer,o=e.mapping===Ms||e.mapping===xa;o?(this._cubemapMaterial===null&&(this._cubemapMaterial=Ig()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Lg());const l=o?this._cubemapMaterial:this._equirectMaterial,d=this._lodMeshes[0];d.material=l;const f=l.uniforms;f.envMap.value=e;const p=this._cubeSize;ua(t,0,0,3*p,2*p),r.setRenderTarget(t),r.render(d,_o)}_applyPMREM(e){const t=this._renderer,r=t.autoClear;t.autoClear=!1;const o=this._lodMeshes.length;for(let l=1;l<o;l++)this._applyGGXFilter(e,l-1,l);t.autoClear=r}_applyGGXFilter(e,t,r){const o=this._renderer,l=this._pingPongRenderTarget,d=this._ggxMaterial,f=this._lodMeshes[r];f.material=d;const p=d.uniforms,m=r/(this._lodMeshes.length-1),_=t/(this._lodMeshes.length-1),S=Math.sqrt(m*m-_*_),x=0+m*1.25,M=S*x,{_lodMax:w}=this,A=this._sizeLods[r],v=3*A*(r>w-Gr?r-w+Gr:0),y=4*(this._cubeSize-A);p.envMap.value=e.texture,p.roughness.value=M,p.mipInt.value=w-t,ua(l,v,y,3*A,2*A),o.setRenderTarget(l),o.render(f,_o),p.envMap.value=l.texture,p.roughness.value=0,p.mipInt.value=w-r,ua(e,v,y,3*A,2*A),o.setRenderTarget(e),o.render(f,_o)}_blur(e,t,r,o,l){const d=this._pingPongRenderTarget;this._halfBlur(e,d,t,r,o,"latitudinal",l),this._halfBlur(d,e,r,r,o,"longitudinal",l)}_halfBlur(e,t,r,o,l,d,f){const p=this._renderer,m=this._blurMaterial;d!=="latitudinal"&&d!=="longitudinal"&&wt("blur direction must be either latitudinal or longitudinal!");const _=3,S=this._lodMeshes[o];S.material=m;const x=m.uniforms,M=this._sizeLods[r]-1,w=isFinite(l)?Math.PI/(2*M):2*Math.PI/(2*_s-1),A=l/w,v=isFinite(l)?1+Math.floor(_*A):_s;v>_s&&rt(`sigmaRadians, ${l}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${_s}`);const y=[];let P=0;for(let D=0;D<_s;++D){const E=D/A,I=Math.exp(-E*E/2);y.push(I),D===0?P+=I:D<v&&(P+=2*I)}for(let D=0;D<y.length;D++)y[D]=y[D]/P;x.envMap.value=e.texture,x.samples.value=v,x.weights.value=y,x.latitudinal.value=d==="latitudinal",f&&(x.poleAxis.value=f);const{_lodMax:U}=this;x.dTheta.value=w,x.mipInt.value=U-r;const N=this._sizeLods[o],L=3*N*(o>U-Gr?o-U+Gr:0),R=4*(this._cubeSize-N);ua(t,L,R,3*N,2*N),p.setRenderTarget(t),p.render(S,_o)}}function cE(s){const e=[],t=[],r=[];let o=s;const l=s-Gr+1+Cg.length;for(let d=0;d<l;d++){const f=Math.pow(2,o);e.push(f);let p=1/f;d>s-Gr?p=Cg[d-s+Gr-1]:d===0&&(p=0),t.push(p);const m=1/(f-2),_=-m,S=1+m,x=[_,_,S,_,S,S,_,_,S,S,_,S],M=6,w=6,A=3,v=2,y=1,P=new Float32Array(A*w*M),U=new Float32Array(v*w*M),N=new Float32Array(y*w*M);for(let R=0;R<M;R++){const D=R%3*2/3-1,E=R>2?0:-1,I=[D,E,0,D+2/3,E,0,D+2/3,E+1,0,D,E,0,D+2/3,E+1,0,D,E+1,0];P.set(I,A*w*R),U.set(x,v*w*R);const z=[R,R,R,R,R,R];N.set(z,y*w*R)}const L=new Vn;L.setAttribute("position",new Ni(P,A)),L.setAttribute("uv",new Ni(U,v)),L.setAttribute("faceIndex",new Ni(N,y)),r.push(new mi(L,null)),o>Gr&&o--}return{lodMeshes:r,sizeLods:e,sigmas:t}}function Pg(s,e,t){const r=new Vi(s,e,t);return r.texture.mapping=Lc,r.texture.name="PMREM.cubeUv",r.scissorTest=!0,r}function ua(s,e,t,r,o){s.viewport.set(e,t,r,o),s.scissor.set(e,t,r,o)}function uE(s,e,t){return new ji({name:"PMREMGGXConvolution",defines:{GGX_SAMPLES:oE,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${s}.0`},uniforms:{envMap:{value:null},roughness:{value:0},mipInt:{value:0}},vertexShader:Dc(),fragmentShader:`

			precision highp float;
			precision highp int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform float roughness;
			uniform float mipInt;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			#define PI 3.14159265359

			// Van der Corput radical inverse
			float radicalInverse_VdC(uint bits) {
				bits = (bits << 16u) | (bits >> 16u);
				bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
				bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
				bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
				bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
				return float(bits) * 2.3283064365386963e-10; // / 0x100000000
			}

			// Hammersley sequence
			vec2 hammersley(uint i, uint N) {
				return vec2(float(i) / float(N), radicalInverse_VdC(i));
			}

			// GGX VNDF importance sampling (Eric Heitz 2018)
			// "Sampling the GGX Distribution of Visible Normals"
			// https://jcgt.org/published/0007/04/01/
			vec3 importanceSampleGGX_VNDF(vec2 Xi, vec3 V, float roughness) {
				float alpha = roughness * roughness;

				// Section 4.1: Orthonormal basis
				vec3 T1 = vec3(1.0, 0.0, 0.0);
				vec3 T2 = cross(V, T1);

				// Section 4.2: Parameterization of projected area
				float r = sqrt(Xi.x);
				float phi = 2.0 * PI * Xi.y;
				float t1 = r * cos(phi);
				float t2 = r * sin(phi);
				float s = 0.5 * (1.0 + V.z);
				t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;

				// Section 4.3: Reprojection onto hemisphere
				vec3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * V;

				// Section 3.4: Transform back to ellipsoid configuration
				return normalize(vec3(alpha * Nh.x, alpha * Nh.y, max(0.0, Nh.z)));
			}

			void main() {
				vec3 N = normalize(vOutputDirection);
				vec3 V = N; // Assume view direction equals normal for pre-filtering

				vec3 prefilteredColor = vec3(0.0);
				float totalWeight = 0.0;

				// For very low roughness, just sample the environment directly
				if (roughness < 0.001) {
					gl_FragColor = vec4(bilinearCubeUV(envMap, N, mipInt), 1.0);
					return;
				}

				// Tangent space basis for VNDF sampling
				vec3 up = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);
				vec3 tangent = normalize(cross(up, N));
				vec3 bitangent = cross(N, tangent);

				for(uint i = 0u; i < uint(GGX_SAMPLES); i++) {
					vec2 Xi = hammersley(i, uint(GGX_SAMPLES));

					// For PMREM, V = N, so in tangent space V is always (0, 0, 1)
					vec3 H_tangent = importanceSampleGGX_VNDF(Xi, vec3(0.0, 0.0, 1.0), roughness);

					// Transform H back to world space
					vec3 H = normalize(tangent * H_tangent.x + bitangent * H_tangent.y + N * H_tangent.z);
					vec3 L = normalize(2.0 * dot(V, H) * H - V);

					float NdotL = max(dot(N, L), 0.0);

					if(NdotL > 0.0) {
						// Sample environment at fixed mip level
						// VNDF importance sampling handles the distribution filtering
						vec3 sampleColor = bilinearCubeUV(envMap, L, mipInt);

						// Weight by NdotL for the split-sum approximation
						// VNDF PDF naturally accounts for the visible microfacet distribution
						prefilteredColor += sampleColor * NdotL;
						totalWeight += NdotL;
					}
				}

				if (totalWeight > 0.0) {
					prefilteredColor = prefilteredColor / totalWeight;
				}

				gl_FragColor = vec4(prefilteredColor, 1.0);
			}
		`,blending:or,depthTest:!1,depthWrite:!1})}function dE(s,e,t){const r=new Float32Array(_s),o=new Y(0,1,0);return new ji({name:"SphericalGaussianBlur",defines:{n:_s,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${s}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:r},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:o}},vertexShader:Dc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:or,depthTest:!1,depthWrite:!1})}function Lg(){return new ji({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Dc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:or,depthTest:!1,depthWrite:!1})}function Ig(){return new ji({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Dc(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:or,depthTest:!1,depthWrite:!1})}function Dc(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}class Yx extends Vi{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const r={width:e,height:e,depth:1},o=[r,r,r,r,r,r];this.texture=new Vx(o),this._setTextureOptions(t),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const r={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},o=new Ro(5,5,5),l=new ji({name:"CubemapFromEquirect",uniforms:_a(r.uniforms),vertexShader:r.vertexShader,fragmentShader:r.fragmentShader,side:Zn,blending:or});l.uniforms.tEquirect.value=t;const d=new mi(o,l),f=t.minFilter;return t.minFilter===ys&&(t.minFilter=In),new g1(1,10,this).update(e,d),t.minFilter=f,d.geometry.dispose(),d.material.dispose(),this}clear(e,t=!0,r=!0,o=!0){const l=e.getRenderTarget();for(let d=0;d<6;d++)e.setRenderTarget(this,d),e.clear(t,r,o);e.setRenderTarget(l)}}function fE(s){let e=new WeakMap,t=new WeakMap,r=null;function o(x,M=!1){return x==null?null:M?d(x):l(x)}function l(x){if(x&&x.isTexture){const M=x.mapping;if(M===Sd||M===Md)if(e.has(x)){const w=e.get(x).texture;return f(w,x.mapping)}else{const w=x.image;if(w&&w.height>0){const A=new Yx(w.height);return A.fromEquirectangularTexture(s,x),e.set(x,A),x.addEventListener("dispose",m),f(A.texture,x.mapping)}else return null}}return x}function d(x){if(x&&x.isTexture){const M=x.mapping,w=M===Sd||M===Md,A=M===Ms||M===xa;if(w||A){let v=t.get(x);const y=v!==void 0?v.texture.pmremVersion:0;if(x.isRenderTargetTexture&&x.pmremVersion!==y)return r===null&&(r=new Rg(s)),v=w?r.fromEquirectangular(x,v):r.fromCubemap(x,v),v.texture.pmremVersion=x.pmremVersion,t.set(x,v),v.texture;if(v!==void 0)return v.texture;{const P=x.image;return w&&P&&P.height>0||A&&P&&p(P)?(r===null&&(r=new Rg(s)),v=w?r.fromEquirectangular(x):r.fromCubemap(x),v.texture.pmremVersion=x.pmremVersion,t.set(x,v),x.addEventListener("dispose",_),v.texture):null}}}return x}function f(x,M){return M===Sd?x.mapping=Ms:M===Md&&(x.mapping=xa),x}function p(x){let M=0;const w=6;for(let A=0;A<w;A++)x[A]!==void 0&&M++;return M===w}function m(x){const M=x.target;M.removeEventListener("dispose",m);const w=e.get(M);w!==void 0&&(e.delete(M),w.dispose())}function _(x){const M=x.target;M.removeEventListener("dispose",_);const w=t.get(M);w!==void 0&&(t.delete(M),w.dispose())}function S(){e=new WeakMap,t=new WeakMap,r!==null&&(r.dispose(),r=null)}return{get:o,dispose:S}}function hE(s){const e={};function t(r){if(e[r]!==void 0)return e[r];const o=s.getExtension(r);return e[r]=o,o}return{has:function(r){return t(r)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(r){const o=t(r);return o===null&&ha("WebGLRenderer: "+r+" extension not supported."),o}}}function pE(s,e,t,r){const o={},l=new WeakMap;function d(S){const x=S.target;x.index!==null&&e.remove(x.index);for(const w in x.attributes)e.remove(x.attributes[w]);x.removeEventListener("dispose",d),delete o[x.id];const M=l.get(x);M&&(e.remove(M),l.delete(x)),r.releaseStatesOfGeometry(x),x.isInstancedBufferGeometry===!0&&delete x._maxInstanceCount,t.memory.geometries--}function f(S,x){return o[x.id]===!0||(x.addEventListener("dispose",d),o[x.id]=!0,t.memory.geometries++),x}function p(S){const x=S.attributes;for(const M in x)e.update(x[M],s.ARRAY_BUFFER)}function m(S){const x=[],M=S.index,w=S.attributes.position;let A=0;if(w===void 0)return;if(M!==null){const P=M.array;A=M.version;for(let U=0,N=P.length;U<N;U+=3){const L=P[U+0],R=P[U+1],D=P[U+2];x.push(L,R,R,D,D,L)}}else{const P=w.array;A=w.version;for(let U=0,N=P.length/3-1;U<N;U+=3){const L=U+0,R=U+1,D=U+2;x.push(L,R,R,D,D,L)}}const v=new(w.count>=65535?kx:Fx)(x,1);v.version=A;const y=l.get(S);y&&e.remove(y),l.set(S,v)}function _(S){const x=l.get(S);if(x){const M=S.index;M!==null&&x.version<M.version&&m(S)}else m(S);return l.get(S)}return{get:f,update:p,getWireframeAttribute:_}}function mE(s,e,t){let r;function o(S){r=S}let l,d;function f(S){l=S.type,d=S.bytesPerElement}function p(S,x){s.drawElements(r,x,l,S*d),t.update(x,r,1)}function m(S,x,M){M!==0&&(s.drawElementsInstanced(r,x,l,S*d,M),t.update(x,r,M))}function _(S,x,M){if(M===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(r,x,0,l,S,0,M);let A=0;for(let v=0;v<M;v++)A+=x[v];t.update(A,r,1)}this.setMode=o,this.setIndex=f,this.render=p,this.renderInstances=m,this.renderMultiDraw=_}function gE(s){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function r(l,d,f){switch(t.calls++,d){case s.TRIANGLES:t.triangles+=f*(l/3);break;case s.LINES:t.lines+=f*(l/2);break;case s.LINE_STRIP:t.lines+=f*(l-1);break;case s.LINE_LOOP:t.lines+=f*l;break;case s.POINTS:t.points+=f*l;break;default:wt("WebGLInfo: Unknown draw mode:",d);break}}function o(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:o,update:r}}function xE(s,e,t){const r=new WeakMap,o=new sn;function l(d,f,p){const m=d.morphTargetInfluences,_=f.morphAttributes.position||f.morphAttributes.normal||f.morphAttributes.color,S=_!==void 0?_.length:0;let x=r.get(f);if(x===void 0||x.count!==S){let z=function(){E.dispose(),r.delete(f),f.removeEventListener("dispose",z)};var M=z;x!==void 0&&x.texture.dispose();const w=f.morphAttributes.position!==void 0,A=f.morphAttributes.normal!==void 0,v=f.morphAttributes.color!==void 0,y=f.morphAttributes.position||[],P=f.morphAttributes.normal||[],U=f.morphAttributes.color||[];let N=0;w===!0&&(N=1),A===!0&&(N=2),v===!0&&(N=3);let L=f.attributes.position.count*N,R=1;L>e.maxTextureSize&&(R=Math.ceil(L/e.maxTextureSize),L=e.maxTextureSize);const D=new Float32Array(L*R*4*S),E=new Ix(D,L,R,S);E.type=Oi,E.needsUpdate=!0;const I=N*4;for(let B=0;B<S;B++){const H=y[B],ce=P[B],he=U[B],Z=L*R*4*B;for(let ue=0;ue<H.count;ue++){const K=ue*I;w===!0&&(o.fromBufferAttribute(H,ue),D[Z+K+0]=o.x,D[Z+K+1]=o.y,D[Z+K+2]=o.z,D[Z+K+3]=0),A===!0&&(o.fromBufferAttribute(ce,ue),D[Z+K+4]=o.x,D[Z+K+5]=o.y,D[Z+K+6]=o.z,D[Z+K+7]=0),v===!0&&(o.fromBufferAttribute(he,ue),D[Z+K+8]=o.x,D[Z+K+9]=o.y,D[Z+K+10]=o.z,D[Z+K+11]=he.itemSize===4?o.w:1)}}x={count:S,texture:E,size:new yt(L,R)},r.set(f,x),f.addEventListener("dispose",z)}if(d.isInstancedMesh===!0&&d.morphTexture!==null)p.getUniforms().setValue(s,"morphTexture",d.morphTexture,t);else{let w=0;for(let v=0;v<m.length;v++)w+=m[v];const A=f.morphTargetsRelative?1:1-w;p.getUniforms().setValue(s,"morphTargetBaseInfluence",A),p.getUniforms().setValue(s,"morphTargetInfluences",m)}p.getUniforms().setValue(s,"morphTargetsTexture",x.texture,t),p.getUniforms().setValue(s,"morphTargetsTextureSize",x.size)}return{update:l}}function vE(s,e,t,r,o){let l=new WeakMap;function d(m){const _=o.render.frame,S=m.geometry,x=e.get(m,S);if(l.get(x)!==_&&(e.update(x),l.set(x,_)),m.isInstancedMesh&&(m.hasEventListener("dispose",p)===!1&&m.addEventListener("dispose",p),l.get(m)!==_&&(t.update(m.instanceMatrix,s.ARRAY_BUFFER),m.instanceColor!==null&&t.update(m.instanceColor,s.ARRAY_BUFFER),l.set(m,_))),m.isSkinnedMesh){const M=m.skeleton;l.get(M)!==_&&(M.update(),l.set(M,_))}return x}function f(){l=new WeakMap}function p(m){const _=m.target;_.removeEventListener("dispose",p),r.releaseStatesOfObject(_),t.remove(_.instanceMatrix),_.instanceColor!==null&&t.remove(_.instanceColor)}return{update:d,dispose:f}}const _E={[xx]:"LINEAR_TONE_MAPPING",[vx]:"REINHARD_TONE_MAPPING",[_x]:"CINEON_TONE_MAPPING",[yx]:"ACES_FILMIC_TONE_MAPPING",[Mx]:"AGX_TONE_MAPPING",[bx]:"NEUTRAL_TONE_MAPPING",[Sx]:"CUSTOM_TONE_MAPPING"};function yE(s,e,t,r,o,l){const d=new Vi(e,t,{type:s,depthBuffer:o,stencilBuffer:l,samples:r?4:0,depthTexture:o?new va(e,t):void 0}),f=new Vi(e,t,{type:ur,depthBuffer:!1,stencilBuffer:!1}),p=new Vn;p.setAttribute("position",new Dn([-1,3,0,-1,-1,0,3,-1,0],3)),p.setAttribute("uv",new Dn([0,2,0,0,2,0],2));const m=new h1({uniforms:{tDiffuse:{value:null}},vertexShader:`
			precision highp float;

			uniform mat4 modelViewMatrix;
			uniform mat4 projectionMatrix;

			attribute vec3 position;
			attribute vec2 uv;

			varying vec2 vUv;

			void main() {
				vUv = uv;
				gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			}`,fragmentShader:`
			precision highp float;

			uniform sampler2D tDiffuse;

			varying vec2 vUv;

			#include <tonemapping_pars_fragment>
			#include <colorspace_pars_fragment>

			void main() {
				gl_FragColor = texture2D( tDiffuse, vUv );

				#ifdef LINEAR_TONE_MAPPING
					gl_FragColor.rgb = LinearToneMapping( gl_FragColor.rgb );
				#elif defined( REINHARD_TONE_MAPPING )
					gl_FragColor.rgb = ReinhardToneMapping( gl_FragColor.rgb );
				#elif defined( CINEON_TONE_MAPPING )
					gl_FragColor.rgb = CineonToneMapping( gl_FragColor.rgb );
				#elif defined( ACES_FILMIC_TONE_MAPPING )
					gl_FragColor.rgb = ACESFilmicToneMapping( gl_FragColor.rgb );
				#elif defined( AGX_TONE_MAPPING )
					gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );
				#elif defined( NEUTRAL_TONE_MAPPING )
					gl_FragColor.rgb = NeutralToneMapping( gl_FragColor.rgb );
				#elif defined( CUSTOM_TONE_MAPPING )
					gl_FragColor.rgb = CustomToneMapping( gl_FragColor.rgb );
				#endif

				#ifdef SRGB_TRANSFER
					gl_FragColor = sRGBTransferOETF( gl_FragColor );
				#endif
			}`,depthTest:!1,depthWrite:!1}),_=new mi(p,m),S=new Wx(-1,1,1,-1,0,1);let x=null,M=null,w=!1,A,v=null,y=[],P=!1;this.setSize=function(U,N){d.setSize(U,N),f.setSize(U,N);for(let L=0;L<y.length;L++){const R=y[L];R.setSize&&R.setSize(U,N)}},this.setEffects=function(U){y=U,P=y.length>0&&y[0].isRenderPass===!0;const N=d.width,L=d.height;for(let R=0;R<y.length;R++){const D=y[R];D.setSize&&D.setSize(N,L)}},this.begin=function(U,N){if(w||U.toneMapping===Bi&&y.length===0)return!1;if(v=N,N!==null){const L=N.width,R=N.height;(d.width!==L||d.height!==R)&&this.setSize(L,R)}return P===!1&&U.setRenderTarget(d),A=U.toneMapping,U.toneMapping=Bi,!0},this.hasRenderPass=function(){return P},this.end=function(U,N){U.toneMapping=A,w=!0;let L=d,R=f;for(let D=0;D<y.length;D++){const E=y[D];if(E.enabled!==!1&&(E.render(U,R,L,N),E.needsSwap!==!1)){const I=L;L=R,R=I}}if(x!==U.outputColorSpace||M!==U.toneMapping){x=U.outputColorSpace,M=U.toneMapping,m.defines={},St.getTransfer(x)===Ft&&(m.defines.SRGB_TRANSFER="");const D=_E[M];D&&(m.defines[D]=""),m.needsUpdate=!0}m.uniforms.tDiffuse.value=L.texture,U.setRenderTarget(v),U.render(_,S),v=null,w=!1},this.isCompositing=function(){return w},this.dispose=function(){d.depthTexture&&d.depthTexture.dispose(),d.dispose(),f.dispose(),p.dispose(),m.dispose()}}const $x=new zn,Yf=new va(1,1),Kx=new Ix,Zx=new zS,Qx=new Vx,Dg=[],Ug=[],Fg=new Float32Array(16),kg=new Float32Array(9),Og=new Float32Array(4);function Ta(s,e,t){const r=s[0];if(r<=0||r>0)return s;const o=e*t;let l=Dg[o];if(l===void 0&&(l=new Float32Array(o),Dg[o]=l),e!==0){r.toArray(l,0);for(let d=1,f=0;d!==e;++d)f+=t,s[d].toArray(l,f)}return l}function hn(s,e){if(s.length!==e.length)return!1;for(let t=0,r=s.length;t<r;t++)if(s[t]!==e[t])return!1;return!0}function pn(s,e){for(let t=0,r=e.length;t<r;t++)s[t]=e[t]}function Uc(s,e){let t=Ug[e];t===void 0&&(t=new Int32Array(e),Ug[e]=t);for(let r=0;r!==e;++r)t[r]=s.allocateTextureUnit();return t}function SE(s,e){const t=this.cache;t[0]!==e&&(s.uniform1f(this.addr,e),t[0]=e)}function ME(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(s.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(hn(t,e))return;s.uniform2fv(this.addr,e),pn(t,e)}}function bE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(s.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(s.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(hn(t,e))return;s.uniform3fv(this.addr,e),pn(t,e)}}function EE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(s.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(hn(t,e))return;s.uniform4fv(this.addr,e),pn(t,e)}}function wE(s,e){const t=this.cache,r=e.elements;if(r===void 0){if(hn(t,e))return;s.uniformMatrix2fv(this.addr,!1,e),pn(t,e)}else{if(hn(t,r))return;Og.set(r),s.uniformMatrix2fv(this.addr,!1,Og),pn(t,r)}}function TE(s,e){const t=this.cache,r=e.elements;if(r===void 0){if(hn(t,e))return;s.uniformMatrix3fv(this.addr,!1,e),pn(t,e)}else{if(hn(t,r))return;kg.set(r),s.uniformMatrix3fv(this.addr,!1,kg),pn(t,r)}}function AE(s,e){const t=this.cache,r=e.elements;if(r===void 0){if(hn(t,e))return;s.uniformMatrix4fv(this.addr,!1,e),pn(t,e)}else{if(hn(t,r))return;Fg.set(r),s.uniformMatrix4fv(this.addr,!1,Fg),pn(t,r)}}function CE(s,e){const t=this.cache;t[0]!==e&&(s.uniform1i(this.addr,e),t[0]=e)}function NE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(s.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(hn(t,e))return;s.uniform2iv(this.addr,e),pn(t,e)}}function RE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(s.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(hn(t,e))return;s.uniform3iv(this.addr,e),pn(t,e)}}function PE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(s.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(hn(t,e))return;s.uniform4iv(this.addr,e),pn(t,e)}}function LE(s,e){const t=this.cache;t[0]!==e&&(s.uniform1ui(this.addr,e),t[0]=e)}function IE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(s.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(hn(t,e))return;s.uniform2uiv(this.addr,e),pn(t,e)}}function DE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(s.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(hn(t,e))return;s.uniform3uiv(this.addr,e),pn(t,e)}}function UE(s,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(s.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(hn(t,e))return;s.uniform4uiv(this.addr,e),pn(t,e)}}function FE(s,e,t){const r=this.cache,o=t.allocateTextureUnit();r[0]!==o&&(s.uniform1i(this.addr,o),r[0]=o);let l;this.type===s.SAMPLER_2D_SHADOW?(Yf.compareFunction=t.isReversedDepthBuffer()?uh:ch,l=Yf):l=$x,t.setTexture2D(e||l,o)}function kE(s,e,t){const r=this.cache,o=t.allocateTextureUnit();r[0]!==o&&(s.uniform1i(this.addr,o),r[0]=o),t.setTexture3D(e||Zx,o)}function OE(s,e,t){const r=this.cache,o=t.allocateTextureUnit();r[0]!==o&&(s.uniform1i(this.addr,o),r[0]=o),t.setTextureCube(e||Qx,o)}function zE(s,e,t){const r=this.cache,o=t.allocateTextureUnit();r[0]!==o&&(s.uniform1i(this.addr,o),r[0]=o),t.setTexture2DArray(e||Kx,o)}function BE(s){switch(s){case 5126:return SE;case 35664:return ME;case 35665:return bE;case 35666:return EE;case 35674:return wE;case 35675:return TE;case 35676:return AE;case 5124:case 35670:return CE;case 35667:case 35671:return NE;case 35668:case 35672:return RE;case 35669:case 35673:return PE;case 5125:return LE;case 36294:return IE;case 36295:return DE;case 36296:return UE;case 35678:case 36198:case 36298:case 36306:case 35682:return FE;case 35679:case 36299:case 36307:return kE;case 35680:case 36300:case 36308:case 36293:return OE;case 36289:case 36303:case 36311:case 36292:return zE}}function VE(s,e){s.uniform1fv(this.addr,e)}function HE(s,e){const t=Ta(e,this.size,2);s.uniform2fv(this.addr,t)}function jE(s,e){const t=Ta(e,this.size,3);s.uniform3fv(this.addr,t)}function GE(s,e){const t=Ta(e,this.size,4);s.uniform4fv(this.addr,t)}function WE(s,e){const t=Ta(e,this.size,4);s.uniformMatrix2fv(this.addr,!1,t)}function XE(s,e){const t=Ta(e,this.size,9);s.uniformMatrix3fv(this.addr,!1,t)}function qE(s,e){const t=Ta(e,this.size,16);s.uniformMatrix4fv(this.addr,!1,t)}function YE(s,e){s.uniform1iv(this.addr,e)}function $E(s,e){s.uniform2iv(this.addr,e)}function KE(s,e){s.uniform3iv(this.addr,e)}function ZE(s,e){s.uniform4iv(this.addr,e)}function QE(s,e){s.uniform1uiv(this.addr,e)}function JE(s,e){s.uniform2uiv(this.addr,e)}function ew(s,e){s.uniform3uiv(this.addr,e)}function tw(s,e){s.uniform4uiv(this.addr,e)}function nw(s,e,t){const r=this.cache,o=e.length,l=Uc(t,o);hn(r,l)||(s.uniform1iv(this.addr,l),pn(r,l));let d;this.type===s.SAMPLER_2D_SHADOW?d=Yf:d=$x;for(let f=0;f!==o;++f)t.setTexture2D(e[f]||d,l[f])}function iw(s,e,t){const r=this.cache,o=e.length,l=Uc(t,o);hn(r,l)||(s.uniform1iv(this.addr,l),pn(r,l));for(let d=0;d!==o;++d)t.setTexture3D(e[d]||Zx,l[d])}function rw(s,e,t){const r=this.cache,o=e.length,l=Uc(t,o);hn(r,l)||(s.uniform1iv(this.addr,l),pn(r,l));for(let d=0;d!==o;++d)t.setTextureCube(e[d]||Qx,l[d])}function sw(s,e,t){const r=this.cache,o=e.length,l=Uc(t,o);hn(r,l)||(s.uniform1iv(this.addr,l),pn(r,l));for(let d=0;d!==o;++d)t.setTexture2DArray(e[d]||Kx,l[d])}function aw(s){switch(s){case 5126:return VE;case 35664:return HE;case 35665:return jE;case 35666:return GE;case 35674:return WE;case 35675:return XE;case 35676:return qE;case 5124:case 35670:return YE;case 35667:case 35671:return $E;case 35668:case 35672:return KE;case 35669:case 35673:return ZE;case 5125:return QE;case 36294:return JE;case 36295:return ew;case 36296:return tw;case 35678:case 36198:case 36298:case 36306:case 35682:return nw;case 35679:case 36299:case 36307:return iw;case 35680:case 36300:case 36308:case 36293:return rw;case 36289:case 36303:case 36311:case 36292:return sw}}class ow{constructor(e,t,r){this.id=e,this.addr=r,this.cache=[],this.type=t.type,this.setValue=BE(t.type)}}class lw{constructor(e,t,r){this.id=e,this.addr=r,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=aw(t.type)}}class cw{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,r){const o=this.seq;for(let l=0,d=o.length;l!==d;++l){const f=o[l];f.setValue(e,t[f.id],r)}}}const Jd=/(\w+)(\])?(\[|\.)?/g;function zg(s,e){s.seq.push(e),s.map[e.id]=e}function uw(s,e,t){const r=s.name,o=r.length;for(Jd.lastIndex=0;;){const l=Jd.exec(r),d=Jd.lastIndex;let f=l[1];const p=l[2]==="]",m=l[3];if(p&&(f=f|0),m===void 0||m==="["&&d+2===o){zg(t,m===void 0?new ow(f,s,e):new lw(f,s,e));break}else{let S=t.map[f];S===void 0&&(S=new cw(f),zg(t,S)),t=S}}}class mc{constructor(e,t){this.seq=[],this.map={};const r=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let d=0;d<r;++d){const f=e.getActiveUniform(t,d),p=e.getUniformLocation(t,f.name);uw(f,p,this)}const o=[],l=[];for(const d of this.seq)d.type===e.SAMPLER_2D_SHADOW||d.type===e.SAMPLER_CUBE_SHADOW||d.type===e.SAMPLER_2D_ARRAY_SHADOW?o.push(d):l.push(d);o.length>0&&(this.seq=o.concat(l))}setValue(e,t,r,o){const l=this.map[t];l!==void 0&&l.setValue(e,r,o)}setOptional(e,t,r){const o=t[r];o!==void 0&&this.setValue(e,r,o)}static upload(e,t,r,o){for(let l=0,d=t.length;l!==d;++l){const f=t[l],p=r[f.id];p.needsUpdate!==!1&&f.setValue(e,p.value,o)}}static seqWithValue(e,t){const r=[];for(let o=0,l=e.length;o!==l;++o){const d=e[o];d.id in t&&r.push(d)}return r}}function Bg(s,e,t){const r=s.createShader(e);return s.shaderSource(r,t),s.compileShader(r),r}const dw=37297;let fw=0;function hw(s,e){const t=s.split(`
`),r=[],o=Math.max(e-6,0),l=Math.min(e+6,t.length);for(let d=o;d<l;d++){const f=d+1;r.push(`${f===e?">":" "} ${f}: ${t[d]}`)}return r.join(`
`)}const Vg=new ut;function pw(s){St._getMatrix(Vg,St.workingColorSpace,s);const e=`mat3( ${Vg.elements.map(t=>t.toFixed(4))} )`;switch(St.getTransfer(s)){case Mc:return[e,"LinearTransferOETF"];case Ft:return[e,"sRGBTransferOETF"];default:return rt("WebGLProgram: Unsupported color space: ",s),[e,"LinearTransferOETF"]}}function Hg(s,e,t){const r=s.getShaderParameter(e,s.COMPILE_STATUS),l=(s.getShaderInfoLog(e)||"").trim();if(r&&l==="")return"";const d=/ERROR: 0:(\d+)/.exec(l);if(d){const f=parseInt(d[1]);return t.toUpperCase()+`

`+l+`

`+hw(s.getShaderSource(e),f)}else return l}function mw(s,e){const t=pw(e);return[`vec4 ${s}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}const gw={[xx]:"Linear",[vx]:"Reinhard",[_x]:"Cineon",[yx]:"ACESFilmic",[Mx]:"AgX",[bx]:"Neutral",[Sx]:"Custom"};function xw(s,e){const t=gw[e];return t===void 0?(rt("WebGLProgram: Unsupported toneMapping:",e),"vec3 "+s+"( vec3 color ) { return LinearToneMapping( color ); }"):"vec3 "+s+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const cc=new Y;function vw(){St.getLuminanceCoefficients(cc);const s=cc.x.toFixed(4),e=cc.y.toFixed(4),t=cc.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${s}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function _w(s){return[s.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",s.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(bo).join(`
`)}function yw(s){const e=[];for(const t in s){const r=s[t];r!==!1&&e.push("#define "+t+" "+r)}return e.join(`
`)}function Sw(s,e){const t={},r=s.getProgramParameter(e,s.ACTIVE_ATTRIBUTES);for(let o=0;o<r;o++){const l=s.getActiveAttrib(e,o),d=l.name;let f=1;l.type===s.FLOAT_MAT2&&(f=2),l.type===s.FLOAT_MAT3&&(f=3),l.type===s.FLOAT_MAT4&&(f=4),t[d]={type:l.type,location:s.getAttribLocation(e,d),locationSize:f}}return t}function bo(s){return s!==""}function jg(s,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return s.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Gg(s,e){return s.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Mw=/^[ \t]*#include +<([\w\d./]+)>/gm;function $f(s){return s.replace(Mw,Ew)}const bw=new Map;function Ew(s,e){let t=pt[e];if(t===void 0){const r=bw.get(e);if(r!==void 0)t=pt[r],rt('WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,r);else throw new Error("THREE.WebGLProgram: Can not resolve #include <"+e+">")}return $f(t)}const ww=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Wg(s){return s.replace(ww,Tw)}function Tw(s,e,t,r){let o="";for(let l=parseInt(e);l<parseInt(t);l++)o+=r.replace(/\[\s*i\s*\]/g,"[ "+l+" ]").replace(/UNROLLED_LOOP_INDEX/g,l);return o}function Xg(s){let e=`precision ${s.precision} float;
	precision ${s.precision} int;
	precision ${s.precision} sampler2D;
	precision ${s.precision} samplerCube;
	precision ${s.precision} sampler3D;
	precision ${s.precision} sampler2DArray;
	precision ${s.precision} sampler2DShadow;
	precision ${s.precision} samplerCubeShadow;
	precision ${s.precision} sampler2DArrayShadow;
	precision ${s.precision} isampler2D;
	precision ${s.precision} isampler3D;
	precision ${s.precision} isamplerCube;
	precision ${s.precision} isampler2DArray;
	precision ${s.precision} usampler2D;
	precision ${s.precision} usampler3D;
	precision ${s.precision} usamplerCube;
	precision ${s.precision} usampler2DArray;
	`;return s.precision==="highp"?e+=`
#define HIGH_PRECISION`:s.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:s.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}const Aw={[uc]:"SHADOWMAP_TYPE_PCF",[So]:"SHADOWMAP_TYPE_VSM"};function Cw(s){return Aw[s.shadowMapType]||"SHADOWMAP_TYPE_BASIC"}const Nw={[Ms]:"ENVMAP_TYPE_CUBE",[xa]:"ENVMAP_TYPE_CUBE",[Lc]:"ENVMAP_TYPE_CUBE_UV"};function Rw(s){return s.envMap===!1?"ENVMAP_TYPE_CUBE":Nw[s.envMapMode]||"ENVMAP_TYPE_CUBE"}const Pw={[xa]:"ENVMAP_MODE_REFRACTION"};function Lw(s){return s.envMap===!1?"ENVMAP_MODE_REFLECTION":Pw[s.envMapMode]||"ENVMAP_MODE_REFLECTION"}const Iw={[gx]:"ENVMAP_BLENDING_MULTIPLY",[vS]:"ENVMAP_BLENDING_MIX",[_S]:"ENVMAP_BLENDING_ADD"};function Dw(s){return s.envMap===!1?"ENVMAP_BLENDING_NONE":Iw[s.combine]||"ENVMAP_BLENDING_NONE"}function Uw(s){const e=s.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,r=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:r,maxMip:t}}function Fw(s,e,t,r){const o=s.getContext(),l=t.defines;let d=t.vertexShader,f=t.fragmentShader;const p=Cw(t),m=Rw(t),_=Lw(t),S=Dw(t),x=Uw(t),M=_w(t),w=yw(l),A=o.createProgram();let v,y,P=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,w].filter(bo).join(`
`),v.length>0&&(v+=`
`),y=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,w].filter(bo).join(`
`),y.length>0&&(y+=`
`)):(v=[Xg(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,w,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+_:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexNormals?"#define HAS_NORMAL":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+p:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",t.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(bo).join(`
`),y=[Xg(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,w,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+m:"",t.envMap?"#define "+_:"",t.envMap?"#define "+S:"",x?"#define CUBEUV_TEXEL_WIDTH "+x.texelWidth:"",x?"#define CUBEUV_TEXEL_HEIGHT "+x.texelHeight:"",x?"#define CUBEUV_MAX_MIP "+x.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.packedNormalMap?"#define USE_PACKED_NORMALMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor?"#define USE_COLOR":"",t.vertexAlphas||t.batchingColor?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+p:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.numLightProbeGrids>0?"#define USE_LIGHT_PROBES_GRID":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",t.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Bi?"#define TONE_MAPPING":"",t.toneMapping!==Bi?pt.tonemapping_pars_fragment:"",t.toneMapping!==Bi?xw("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",pt.colorspace_pars_fragment,mw("linearToOutputTexel",t.outputColorSpace),vw(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(bo).join(`
`)),d=$f(d),d=jg(d,t),d=Gg(d,t),f=$f(f),f=jg(f,t),f=Gg(f,t),d=Wg(d),f=Wg(f),t.isRawShaderMaterial!==!0&&(P=`#version 300 es
`,v=[M,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,y=["#define varying in",t.glslVersion===ng?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===ng?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+y);const U=P+v+d,N=P+y+f,L=Bg(o,o.VERTEX_SHADER,U),R=Bg(o,o.FRAGMENT_SHADER,N);o.attachShader(A,L),o.attachShader(A,R),t.index0AttributeName!==void 0?o.bindAttribLocation(A,0,t.index0AttributeName):t.hasPositionAttribute===!0&&o.bindAttribLocation(A,0,"position"),o.linkProgram(A);function D(B){if(s.debug.checkShaderErrors){const H=o.getProgramInfoLog(A)||"",ce=o.getShaderInfoLog(L)||"",he=o.getShaderInfoLog(R)||"",Z=H.trim(),ue=ce.trim(),K=he.trim();let q=!0,se=!0;if(o.getProgramParameter(A,o.LINK_STATUS)===!1)if(q=!1,typeof s.debug.onShaderError=="function")s.debug.onShaderError(o,A,L,R);else{const le=Hg(o,L,"vertex"),k=Hg(o,R,"fragment");wt("WebGLProgram: Shader Error "+o.getError()+" - VALIDATE_STATUS "+o.getProgramParameter(A,o.VALIDATE_STATUS)+`

Material Name: `+B.name+`
Material Type: `+B.type+`

Program Info Log: `+Z+`
`+le+`
`+k)}else Z!==""?rt("WebGLProgram: Program Info Log:",Z):(ue===""||K==="")&&(se=!1);se&&(B.diagnostics={runnable:q,programLog:Z,vertexShader:{log:ue,prefix:v},fragmentShader:{log:K,prefix:y}})}o.deleteShader(L),o.deleteShader(R),E=new mc(o,A),I=Sw(o,A)}let E;this.getUniforms=function(){return E===void 0&&D(this),E};let I;this.getAttributes=function(){return I===void 0&&D(this),I};let z=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return z===!1&&(z=o.getProgramParameter(A,dw)),z},this.destroy=function(){r.releaseStatesOfProgram(this),o.deleteProgram(A),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=fw++,this.cacheKey=e,this.usedTimes=1,this.program=A,this.vertexShader=L,this.fragmentShader=R,this}let kw=0;class Ow{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e,t,r){const o=this._getShaderCacheForMaterial(e);return o.has(t)===!1&&(o.add(t),t.usedTimes++),o.has(r)===!1&&(o.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const r of t)r.usedTimes--,r.usedTimes===0&&this.shaderCache.delete(r.code);return this.materialCache.delete(e),this}getVertexShaderStage(e){return this._getShaderStage(e.vertexShader)}getFragmentShaderStage(e){return this._getShaderStage(e.fragmentShader)}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let r=t.get(e);return r===void 0&&(r=new Set,t.set(e,r)),r}_getShaderStage(e){const t=this.shaderCache;let r=t.get(e);return r===void 0&&(r=new zw(e),t.set(e,r)),r}}class zw{constructor(e){this.id=kw++,this.code=e,this.usedTimes=0}}function Bw(s){return s===bs||s===_c||s===yc}function Vw(s,e,t,r,o,l){const d=new Dx,f=new Ow,p=new Set,m=[],_=new Map,S=r.logarithmicDepthBuffer;let x=r.precision;const M={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distance",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function w(E){return p.add(E),E===0?"uv":`uv${E}`}function A(E,I,z,B,H,ce){const he=B.fog,Z=H.geometry,ue=E.isMeshStandardMaterial||E.isMeshLambertMaterial||E.isMeshPhongMaterial?B.environment:null,K=E.isMeshStandardMaterial||E.isMeshLambertMaterial&&!E.envMap||E.isMeshPhongMaterial&&!E.envMap,q=e.get(E.envMap||ue,K),se=q&&q.mapping===Lc?q.image.height:null,le=M[E.type];E.precision!==null&&(x=r.getMaxPrecision(E.precision),x!==E.precision&&rt("WebGLProgram.getParameters:",E.precision,"not supported, using",x,"instead."));const k=Z.morphAttributes.position||Z.morphAttributes.normal||Z.morphAttributes.color,Q=k!==void 0?k.length:0;let Ue=0;Z.morphAttributes.position!==void 0&&(Ue=1),Z.morphAttributes.normal!==void 0&&(Ue=2),Z.morphAttributes.color!==void 0&&(Ue=3);let $e,Ve,re,_e;if(le){const He=ki[le];$e=He.vertexShader,Ve=He.fragmentShader}else{$e=E.vertexShader,Ve=E.fragmentShader;const He=f.getVertexShaderStage(E),kt=f.getFragmentShaderStage(E);f.update(E,He,kt),re=He.id,_e=kt.id}const me=s.getRenderTarget(),Fe=s.state.buffers.depth.getReversed(),Je=H.isInstancedMesh===!0,et=H.isBatchedMesh===!0,Wt=!!E.map,ft=!!E.matcap,Nt=!!q,Mt=!!E.aoMap,_t=!!E.lightMap,Xt=!!E.bumpMap&&E.wireframe===!1,tn=!!E.normalMap,nn=!!E.displacementMap,Kt=!!E.emissiveMap,It=!!E.metalnessMap,qt=!!E.roughnessMap,W=E.anisotropy>0,_n=E.clearcoat>0,Tt=E.dispersion>0,F=E.iridescence>0,b=E.sheen>0,$=E.transmission>0,ie=W&&!!E.anisotropyMap,de=_n&&!!E.clearcoatMap,be=_n&&!!E.clearcoatNormalMap,Ne=_n&&!!E.clearcoatRoughnessMap,fe=F&&!!E.iridescenceMap,ge=F&&!!E.iridescenceThicknessMap,Pe=b&&!!E.sheenColorMap,qe=b&&!!E.sheenRoughnessMap,Le=!!E.specularMap,Ce=!!E.specularColorMap,Qe=!!E.specularIntensityMap,tt=$&&!!E.transmissionMap,at=$&&!!E.thicknessMap,j=!!E.gradientMap,Ae=!!E.alphaMap,pe=E.alphaTest>0,Re=!!E.alphaHash,Ie=!!E.extensions;let ve=Bi;E.toneMapped&&(me===null||me.isXRRenderTarget===!0)&&(ve=s.toneMapping);const Ge={shaderID:le,shaderType:E.type,shaderName:E.name,vertexShader:$e,fragmentShader:Ve,defines:E.defines,customVertexShaderID:re,customFragmentShaderID:_e,isRawShaderMaterial:E.isRawShaderMaterial===!0,glslVersion:E.glslVersion,precision:x,batching:et,batchingColor:et&&H._colorsTexture!==null,instancing:Je,instancingColor:Je&&H.instanceColor!==null,instancingMorph:Je&&H.morphTexture!==null,outputColorSpace:me===null?s.outputColorSpace:me.isXRRenderTarget===!0?me.texture.colorSpace:St.workingColorSpace,alphaToCoverage:!!E.alphaToCoverage,map:Wt,matcap:ft,envMap:Nt,envMapMode:Nt&&q.mapping,envMapCubeUVHeight:se,aoMap:Mt,lightMap:_t,bumpMap:Xt,normalMap:tn,displacementMap:nn,emissiveMap:Kt,normalMapObjectSpace:tn&&E.normalMapType===MS,normalMapTangentSpace:tn&&E.normalMapType===Jm,packedNormalMap:tn&&E.normalMapType===Jm&&Bw(E.normalMap.format),metalnessMap:It,roughnessMap:qt,anisotropy:W,anisotropyMap:ie,clearcoat:_n,clearcoatMap:de,clearcoatNormalMap:be,clearcoatRoughnessMap:Ne,dispersion:Tt,iridescence:F,iridescenceMap:fe,iridescenceThicknessMap:ge,sheen:b,sheenColorMap:Pe,sheenRoughnessMap:qe,specularMap:Le,specularColorMap:Ce,specularIntensityMap:Qe,transmission:$,transmissionMap:tt,thicknessMap:at,gradientMap:j,opaque:E.transparent===!1&&E.blending===fa&&E.alphaToCoverage===!1,alphaMap:Ae,alphaTest:pe,alphaHash:Re,combine:E.combine,mapUv:Wt&&w(E.map.channel),aoMapUv:Mt&&w(E.aoMap.channel),lightMapUv:_t&&w(E.lightMap.channel),bumpMapUv:Xt&&w(E.bumpMap.channel),normalMapUv:tn&&w(E.normalMap.channel),displacementMapUv:nn&&w(E.displacementMap.channel),emissiveMapUv:Kt&&w(E.emissiveMap.channel),metalnessMapUv:It&&w(E.metalnessMap.channel),roughnessMapUv:qt&&w(E.roughnessMap.channel),anisotropyMapUv:ie&&w(E.anisotropyMap.channel),clearcoatMapUv:de&&w(E.clearcoatMap.channel),clearcoatNormalMapUv:be&&w(E.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Ne&&w(E.clearcoatRoughnessMap.channel),iridescenceMapUv:fe&&w(E.iridescenceMap.channel),iridescenceThicknessMapUv:ge&&w(E.iridescenceThicknessMap.channel),sheenColorMapUv:Pe&&w(E.sheenColorMap.channel),sheenRoughnessMapUv:qe&&w(E.sheenRoughnessMap.channel),specularMapUv:Le&&w(E.specularMap.channel),specularColorMapUv:Ce&&w(E.specularColorMap.channel),specularIntensityMapUv:Qe&&w(E.specularIntensityMap.channel),transmissionMapUv:tt&&w(E.transmissionMap.channel),thicknessMapUv:at&&w(E.thicknessMap.channel),alphaMapUv:Ae&&w(E.alphaMap.channel),vertexTangents:!!Z.attributes.tangent&&(tn||W),vertexNormals:!!Z.attributes.normal,vertexColors:E.vertexColors,vertexAlphas:E.vertexColors===!0&&!!Z.attributes.color&&Z.attributes.color.itemSize===4,pointsUvs:H.isPoints===!0&&!!Z.attributes.uv&&(Wt||Ae),fog:!!he,useFog:E.fog===!0,fogExp2:!!he&&he.isFogExp2,flatShading:E.wireframe===!1&&(E.flatShading===!0||Z.attributes.normal===void 0&&tn===!1&&(E.isMeshLambertMaterial||E.isMeshPhongMaterial||E.isMeshStandardMaterial||E.isMeshPhysicalMaterial)),sizeAttenuation:E.sizeAttenuation===!0,logarithmicDepthBuffer:S,reversedDepthBuffer:Fe,skinning:H.isSkinnedMesh===!0,hasPositionAttribute:Z.attributes.position!==void 0,morphTargets:Z.morphAttributes.position!==void 0,morphNormals:Z.morphAttributes.normal!==void 0,morphColors:Z.morphAttributes.color!==void 0,morphTargetsCount:Q,morphTextureStride:Ue,numDirLights:I.directional.length,numPointLights:I.point.length,numSpotLights:I.spot.length,numSpotLightMaps:I.spotLightMap.length,numRectAreaLights:I.rectArea.length,numHemiLights:I.hemi.length,numDirLightShadows:I.directionalShadowMap.length,numPointLightShadows:I.pointShadowMap.length,numSpotLightShadows:I.spotShadowMap.length,numSpotLightShadowsWithMaps:I.numSpotLightShadowsWithMaps,numLightProbes:I.numLightProbes,numLightProbeGrids:ce.length,numClippingPlanes:l.numPlanes,numClipIntersection:l.numIntersection,dithering:E.dithering,shadowMapEnabled:s.shadowMap.enabled&&z.length>0,shadowMapType:s.shadowMap.type,toneMapping:ve,decodeVideoTexture:Wt&&E.map.isVideoTexture===!0&&St.getTransfer(E.map.colorSpace)===Ft,decodeVideoTextureEmissive:Kt&&E.emissiveMap.isVideoTexture===!0&&St.getTransfer(E.emissiveMap.colorSpace)===Ft,premultipliedAlpha:E.premultipliedAlpha,doubleSided:E.side===sr,flipSided:E.side===Zn,useDepthPacking:E.depthPacking>=0,depthPacking:E.depthPacking||0,index0AttributeName:E.index0AttributeName,extensionClipCullDistance:Ie&&E.extensions.clipCullDistance===!0&&t.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Ie&&E.extensions.multiDraw===!0||et)&&t.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:t.has("KHR_parallel_shader_compile"),customProgramCacheKey:E.customProgramCacheKey()};return Ge.vertexUv1s=p.has(1),Ge.vertexUv2s=p.has(2),Ge.vertexUv3s=p.has(3),p.clear(),Ge}function v(E){const I=[];if(E.shaderID?I.push(E.shaderID):(I.push(E.customVertexShaderID),I.push(E.customFragmentShaderID)),E.defines!==void 0)for(const z in E.defines)I.push(z),I.push(E.defines[z]);return E.isRawShaderMaterial===!1&&(y(I,E),P(I,E),I.push(s.outputColorSpace)),I.push(E.customProgramCacheKey),I.join()}function y(E,I){E.push(I.precision),E.push(I.outputColorSpace),E.push(I.envMapMode),E.push(I.envMapCubeUVHeight),E.push(I.mapUv),E.push(I.alphaMapUv),E.push(I.lightMapUv),E.push(I.aoMapUv),E.push(I.bumpMapUv),E.push(I.normalMapUv),E.push(I.displacementMapUv),E.push(I.emissiveMapUv),E.push(I.metalnessMapUv),E.push(I.roughnessMapUv),E.push(I.anisotropyMapUv),E.push(I.clearcoatMapUv),E.push(I.clearcoatNormalMapUv),E.push(I.clearcoatRoughnessMapUv),E.push(I.iridescenceMapUv),E.push(I.iridescenceThicknessMapUv),E.push(I.sheenColorMapUv),E.push(I.sheenRoughnessMapUv),E.push(I.specularMapUv),E.push(I.specularColorMapUv),E.push(I.specularIntensityMapUv),E.push(I.transmissionMapUv),E.push(I.thicknessMapUv),E.push(I.combine),E.push(I.fogExp2),E.push(I.sizeAttenuation),E.push(I.morphTargetsCount),E.push(I.morphAttributeCount),E.push(I.numDirLights),E.push(I.numPointLights),E.push(I.numSpotLights),E.push(I.numSpotLightMaps),E.push(I.numHemiLights),E.push(I.numRectAreaLights),E.push(I.numDirLightShadows),E.push(I.numPointLightShadows),E.push(I.numSpotLightShadows),E.push(I.numSpotLightShadowsWithMaps),E.push(I.numLightProbes),E.push(I.shadowMapType),E.push(I.toneMapping),E.push(I.numClippingPlanes),E.push(I.numClipIntersection),E.push(I.depthPacking)}function P(E,I){d.disableAll(),I.instancing&&d.enable(0),I.instancingColor&&d.enable(1),I.instancingMorph&&d.enable(2),I.matcap&&d.enable(3),I.envMap&&d.enable(4),I.normalMapObjectSpace&&d.enable(5),I.normalMapTangentSpace&&d.enable(6),I.clearcoat&&d.enable(7),I.iridescence&&d.enable(8),I.alphaTest&&d.enable(9),I.vertexColors&&d.enable(10),I.vertexAlphas&&d.enable(11),I.vertexUv1s&&d.enable(12),I.vertexUv2s&&d.enable(13),I.vertexUv3s&&d.enable(14),I.vertexTangents&&d.enable(15),I.anisotropy&&d.enable(16),I.alphaHash&&d.enable(17),I.batching&&d.enable(18),I.dispersion&&d.enable(19),I.batchingColor&&d.enable(20),I.gradientMap&&d.enable(21),I.packedNormalMap&&d.enable(22),I.vertexNormals&&d.enable(23),E.push(d.mask),d.disableAll(),I.fog&&d.enable(0),I.useFog&&d.enable(1),I.flatShading&&d.enable(2),I.logarithmicDepthBuffer&&d.enable(3),I.reversedDepthBuffer&&d.enable(4),I.skinning&&d.enable(5),I.morphTargets&&d.enable(6),I.morphNormals&&d.enable(7),I.morphColors&&d.enable(8),I.premultipliedAlpha&&d.enable(9),I.shadowMapEnabled&&d.enable(10),I.doubleSided&&d.enable(11),I.flipSided&&d.enable(12),I.useDepthPacking&&d.enable(13),I.dithering&&d.enable(14),I.transmission&&d.enable(15),I.sheen&&d.enable(16),I.opaque&&d.enable(17),I.pointsUvs&&d.enable(18),I.decodeVideoTexture&&d.enable(19),I.decodeVideoTextureEmissive&&d.enable(20),I.alphaToCoverage&&d.enable(21),I.numLightProbeGrids>0&&d.enable(22),I.hasPositionAttribute&&d.enable(23),E.push(d.mask)}function U(E){const I=M[E.type];let z;if(I){const B=ki[I];z=u1.clone(B.uniforms)}else z=E.uniforms;return z}function N(E,I){let z=_.get(I);return z!==void 0?++z.usedTimes:(z=new Fw(s,I,E,o),m.push(z),_.set(I,z)),z}function L(E){if(--E.usedTimes===0){const I=m.indexOf(E);m[I]=m[m.length-1],m.pop(),_.delete(E.cacheKey),E.destroy()}}function R(E){f.remove(E)}function D(){f.dispose()}return{getParameters:A,getProgramCacheKey:v,getUniforms:U,acquireProgram:N,releaseProgram:L,releaseShaderCache:R,programs:m,dispose:D}}function Hw(){let s=new WeakMap;function e(d){return s.has(d)}function t(d){let f=s.get(d);return f===void 0&&(f={},s.set(d,f)),f}function r(d){s.delete(d)}function o(d,f,p){s.get(d)[f]=p}function l(){s=new WeakMap}return{has:e,get:t,remove:r,update:o,dispose:l}}function jw(s,e){return s.groupOrder!==e.groupOrder?s.groupOrder-e.groupOrder:s.renderOrder!==e.renderOrder?s.renderOrder-e.renderOrder:s.material.id!==e.material.id?s.material.id-e.material.id:s.materialVariant!==e.materialVariant?s.materialVariant-e.materialVariant:s.z!==e.z?s.z-e.z:s.id-e.id}function qg(s,e){return s.groupOrder!==e.groupOrder?s.groupOrder-e.groupOrder:s.renderOrder!==e.renderOrder?s.renderOrder-e.renderOrder:s.z!==e.z?e.z-s.z:s.id-e.id}function Yg(){const s=[];let e=0;const t=[],r=[],o=[];function l(){e=0,t.length=0,r.length=0,o.length=0}function d(x){let M=0;return x.isInstancedMesh&&(M+=2),x.isSkinnedMesh&&(M+=1),M}function f(x,M,w,A,v,y){let P=s[e];return P===void 0?(P={id:x.id,object:x,geometry:M,material:w,materialVariant:d(x),groupOrder:A,renderOrder:x.renderOrder,z:v,group:y},s[e]=P):(P.id=x.id,P.object=x,P.geometry=M,P.material=w,P.materialVariant=d(x),P.groupOrder=A,P.renderOrder=x.renderOrder,P.z=v,P.group=y),e++,P}function p(x,M,w,A,v,y){const P=f(x,M,w,A,v,y);w.transmission>0?r.push(P):w.transparent===!0?o.push(P):t.push(P)}function m(x,M,w,A,v,y){const P=f(x,M,w,A,v,y);w.transmission>0?r.unshift(P):w.transparent===!0?o.unshift(P):t.unshift(P)}function _(x,M,w){t.length>1&&t.sort(x||jw),r.length>1&&r.sort(M||qg),o.length>1&&o.sort(M||qg),w&&(t.reverse(),r.reverse(),o.reverse())}function S(){for(let x=e,M=s.length;x<M;x++){const w=s[x];if(w.id===null)break;w.id=null,w.object=null,w.geometry=null,w.material=null,w.group=null}}return{opaque:t,transmissive:r,transparent:o,init:l,push:p,unshift:m,finish:S,sort:_}}function Gw(){let s=new WeakMap;function e(r,o){const l=s.get(r);let d;return l===void 0?(d=new Yg,s.set(r,[d])):o>=l.length?(d=new Yg,l.push(d)):d=l[o],d}function t(){s=new WeakMap}return{get:e,dispose:t}}function Ww(){const s={};return{get:function(e){if(s[e.id]!==void 0)return s[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new Y,color:new Ct};break;case"SpotLight":t={position:new Y,direction:new Y,color:new Ct,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new Y,color:new Ct,distance:0,decay:0};break;case"HemisphereLight":t={direction:new Y,skyColor:new Ct,groundColor:new Ct};break;case"RectAreaLight":t={color:new Ct,position:new Y,halfWidth:new Y,halfHeight:new Y};break}return s[e.id]=t,t}}}function Xw(){const s={};return{get:function(e){if(s[e.id]!==void 0)return s[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new yt};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new yt};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new yt,shadowCameraNear:1,shadowCameraFar:1e3};break}return s[e.id]=t,t}}}let qw=0;function Yw(s,e){return(e.castShadow?2:0)-(s.castShadow?2:0)+(e.map?1:0)-(s.map?1:0)}function $w(s){const e=new Ww,t=Xw(),r={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let m=0;m<9;m++)r.probe.push(new Y);const o=new Y,l=new en,d=new en;function f(m){let _=0,S=0,x=0;for(let I=0;I<9;I++)r.probe[I].set(0,0,0);let M=0,w=0,A=0,v=0,y=0,P=0,U=0,N=0,L=0,R=0,D=0;m.sort(Yw);for(let I=0,z=m.length;I<z;I++){const B=m[I],H=B.color,ce=B.intensity,he=B.distance;let Z=null;if(B.shadow&&B.shadow.map&&(B.shadow.map.texture.format===bs?Z=B.shadow.map.texture:Z=B.shadow.map.depthTexture||B.shadow.map.texture),B.isAmbientLight)_+=H.r*ce,S+=H.g*ce,x+=H.b*ce;else if(B.isLightProbe){for(let ue=0;ue<9;ue++)r.probe[ue].addScaledVector(B.sh.coefficients[ue],ce);D++}else if(B.isDirectionalLight){const ue=e.get(B);if(ue.color.copy(B.color).multiplyScalar(B.intensity),B.castShadow){const K=B.shadow,q=t.get(B);q.shadowIntensity=K.intensity,q.shadowBias=K.bias,q.shadowNormalBias=K.normalBias,q.shadowRadius=K.radius,q.shadowMapSize=K.mapSize,r.directionalShadow[M]=q,r.directionalShadowMap[M]=Z,r.directionalShadowMatrix[M]=B.shadow.matrix,P++}r.directional[M]=ue,M++}else if(B.isSpotLight){const ue=e.get(B);ue.position.setFromMatrixPosition(B.matrixWorld),ue.color.copy(H).multiplyScalar(ce),ue.distance=he,ue.coneCos=Math.cos(B.angle),ue.penumbraCos=Math.cos(B.angle*(1-B.penumbra)),ue.decay=B.decay,r.spot[A]=ue;const K=B.shadow;if(B.map&&(r.spotLightMap[L]=B.map,L++,K.updateMatrices(B),B.castShadow&&R++),r.spotLightMatrix[A]=K.matrix,B.castShadow){const q=t.get(B);q.shadowIntensity=K.intensity,q.shadowBias=K.bias,q.shadowNormalBias=K.normalBias,q.shadowRadius=K.radius,q.shadowMapSize=K.mapSize,r.spotShadow[A]=q,r.spotShadowMap[A]=Z,N++}A++}else if(B.isRectAreaLight){const ue=e.get(B);ue.color.copy(H).multiplyScalar(ce),ue.halfWidth.set(B.width*.5,0,0),ue.halfHeight.set(0,B.height*.5,0),r.rectArea[v]=ue,v++}else if(B.isPointLight){const ue=e.get(B);if(ue.color.copy(B.color).multiplyScalar(B.intensity),ue.distance=B.distance,ue.decay=B.decay,B.castShadow){const K=B.shadow,q=t.get(B);q.shadowIntensity=K.intensity,q.shadowBias=K.bias,q.shadowNormalBias=K.normalBias,q.shadowRadius=K.radius,q.shadowMapSize=K.mapSize,q.shadowCameraNear=K.camera.near,q.shadowCameraFar=K.camera.far,r.pointShadow[w]=q,r.pointShadowMap[w]=Z,r.pointShadowMatrix[w]=B.shadow.matrix,U++}r.point[w]=ue,w++}else if(B.isHemisphereLight){const ue=e.get(B);ue.skyColor.copy(B.color).multiplyScalar(ce),ue.groundColor.copy(B.groundColor).multiplyScalar(ce),r.hemi[y]=ue,y++}}v>0&&(s.has("OES_texture_float_linear")===!0?(r.rectAreaLTC1=De.LTC_FLOAT_1,r.rectAreaLTC2=De.LTC_FLOAT_2):(r.rectAreaLTC1=De.LTC_HALF_1,r.rectAreaLTC2=De.LTC_HALF_2)),r.ambient[0]=_,r.ambient[1]=S,r.ambient[2]=x;const E=r.hash;(E.directionalLength!==M||E.pointLength!==w||E.spotLength!==A||E.rectAreaLength!==v||E.hemiLength!==y||E.numDirectionalShadows!==P||E.numPointShadows!==U||E.numSpotShadows!==N||E.numSpotMaps!==L||E.numLightProbes!==D)&&(r.directional.length=M,r.spot.length=A,r.rectArea.length=v,r.point.length=w,r.hemi.length=y,r.directionalShadow.length=P,r.directionalShadowMap.length=P,r.pointShadow.length=U,r.pointShadowMap.length=U,r.spotShadow.length=N,r.spotShadowMap.length=N,r.directionalShadowMatrix.length=P,r.pointShadowMatrix.length=U,r.spotLightMatrix.length=N+L-R,r.spotLightMap.length=L,r.numSpotLightShadowsWithMaps=R,r.numLightProbes=D,E.directionalLength=M,E.pointLength=w,E.spotLength=A,E.rectAreaLength=v,E.hemiLength=y,E.numDirectionalShadows=P,E.numPointShadows=U,E.numSpotShadows=N,E.numSpotMaps=L,E.numLightProbes=D,r.version=qw++)}function p(m,_){let S=0,x=0,M=0,w=0,A=0;const v=_.matrixWorldInverse;for(let y=0,P=m.length;y<P;y++){const U=m[y];if(U.isDirectionalLight){const N=r.directional[S];N.direction.setFromMatrixPosition(U.matrixWorld),o.setFromMatrixPosition(U.target.matrixWorld),N.direction.sub(o),N.direction.transformDirection(v),S++}else if(U.isSpotLight){const N=r.spot[M];N.position.setFromMatrixPosition(U.matrixWorld),N.position.applyMatrix4(v),N.direction.setFromMatrixPosition(U.matrixWorld),o.setFromMatrixPosition(U.target.matrixWorld),N.direction.sub(o),N.direction.transformDirection(v),M++}else if(U.isRectAreaLight){const N=r.rectArea[w];N.position.setFromMatrixPosition(U.matrixWorld),N.position.applyMatrix4(v),d.identity(),l.copy(U.matrixWorld),l.premultiply(v),d.extractRotation(l),N.halfWidth.set(U.width*.5,0,0),N.halfHeight.set(0,U.height*.5,0),N.halfWidth.applyMatrix4(d),N.halfHeight.applyMatrix4(d),w++}else if(U.isPointLight){const N=r.point[x];N.position.setFromMatrixPosition(U.matrixWorld),N.position.applyMatrix4(v),x++}else if(U.isHemisphereLight){const N=r.hemi[A];N.direction.setFromMatrixPosition(U.matrixWorld),N.direction.transformDirection(v),A++}}}return{setup:f,setupView:p,state:r}}function $g(s){const e=new $w(s),t=[],r=[],o=[];function l(x){S.camera=x,t.length=0,r.length=0,o.length=0}function d(x){t.push(x)}function f(x){r.push(x)}function p(x){o.push(x)}function m(){e.setup(t)}function _(x){e.setupView(t,x)}const S={lightsArray:t,shadowsArray:r,lightProbeGridArray:o,camera:null,lights:e,transmissionRenderTarget:{},textureUnits:0};return{init:l,state:S,setupLights:m,setupLightsView:_,pushLight:d,pushShadow:f,pushLightProbeGrid:p}}function Kw(s){let e=new WeakMap;function t(o,l=0){const d=e.get(o);let f;return d===void 0?(f=new $g(s),e.set(o,[f])):l>=d.length?(f=new $g(s),d.push(f)):f=d[l],f}function r(){e=new WeakMap}return{get:t,dispose:r}}const Zw=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Qw=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ).rg;
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ).r;
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( max( 0.0, squared_mean - mean * mean ) );
	gl_FragColor = vec4( mean, std_dev, 0.0, 1.0 );
}`,Jw=[new Y(1,0,0),new Y(-1,0,0),new Y(0,1,0),new Y(0,-1,0),new Y(0,0,1),new Y(0,0,-1)],eT=[new Y(0,-1,0),new Y(0,-1,0),new Y(0,0,1),new Y(0,0,-1),new Y(0,-1,0),new Y(0,-1,0)],Kg=new en,yo=new Y,ef=new Y;function tT(s,e,t){let r=new Ox;const o=new yt,l=new yt,d=new sn,f=new p1,p=new m1,m={},_=t.maxTextureSize,S={[Xr]:Zn,[Zn]:Xr,[sr]:sr},x=new ji({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new yt},radius:{value:4}},vertexShader:Zw,fragmentShader:Qw}),M=x.clone();M.defines.HORIZONTAL_PASS=1;const w=new Vn;w.setAttribute("position",new Ni(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const A=new mi(w,x),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=uc;let y=this.type;this.render=function(R,D,E){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||R.length===0)return;this.type===Jy&&(rt("WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead."),this.type=uc);const I=s.getRenderTarget(),z=s.getActiveCubeFace(),B=s.getActiveMipmapLevel(),H=s.state;H.setBlending(or),H.buffers.depth.getReversed()===!0?H.buffers.color.setClear(0,0,0,0):H.buffers.color.setClear(1,1,1,1),H.buffers.depth.setTest(!0),H.setScissorTest(!1);const ce=y!==this.type;ce&&D.traverse(function(he){he.material&&(Array.isArray(he.material)?he.material.forEach(Z=>Z.needsUpdate=!0):he.material.needsUpdate=!0)});for(let he=0,Z=R.length;he<Z;he++){const ue=R[he],K=ue.shadow;if(K===void 0){rt("WebGLShadowMap:",ue,"has no shadow.");continue}if(K.autoUpdate===!1&&K.needsUpdate===!1)continue;o.copy(K.mapSize);const q=K.getFrameExtents();o.multiply(q),l.copy(K.mapSize),(o.x>_||o.y>_)&&(o.x>_&&(l.x=Math.floor(_/q.x),o.x=l.x*q.x,K.mapSize.x=l.x),o.y>_&&(l.y=Math.floor(_/q.y),o.y=l.y*q.y,K.mapSize.y=l.y));const se=s.state.buffers.depth.getReversed();if(K.camera._reversedDepth=se,K.map===null||ce===!0){if(K.map!==null&&(K.map.depthTexture!==null&&(K.map.depthTexture.dispose(),K.map.depthTexture=null),K.map.dispose()),this.type===So){if(ue.isPointLight){rt("WebGLShadowMap: VSM shadow maps are not supported for PointLights. Use PCF or BasicShadowMap instead.");continue}K.map=new Vi(o.x,o.y,{format:bs,type:ur,minFilter:In,magFilter:In,generateMipmaps:!1}),K.map.texture.name=ue.name+".shadowMap",K.map.depthTexture=new va(o.x,o.y,Oi),K.map.depthTexture.name=ue.name+".shadowMapDepth",K.map.depthTexture.format=dr,K.map.depthTexture.compareFunction=null,K.map.depthTexture.minFilter=wn,K.map.depthTexture.magFilter=wn}else ue.isPointLight?(K.map=new Yx(o.x),K.map.depthTexture=new a1(o.x,Hi)):(K.map=new Vi(o.x,o.y),K.map.depthTexture=new va(o.x,o.y,Hi)),K.map.depthTexture.name=ue.name+".shadowMap",K.map.depthTexture.format=dr,this.type===uc?(K.map.depthTexture.compareFunction=se?uh:ch,K.map.depthTexture.minFilter=In,K.map.depthTexture.magFilter=In):(K.map.depthTexture.compareFunction=null,K.map.depthTexture.minFilter=wn,K.map.depthTexture.magFilter=wn);K.camera.updateProjectionMatrix()}const le=K.map.isWebGLCubeRenderTarget?6:1;for(let k=0;k<le;k++){if(K.map.isWebGLCubeRenderTarget)s.setRenderTarget(K.map,k),s.clear();else{k===0&&(s.setRenderTarget(K.map),s.clear());const Q=K.getViewport(k);d.set(l.x*Q.x,l.y*Q.y,l.x*Q.z,l.y*Q.w),H.viewport(d)}if(ue.isPointLight){const Q=K.camera,Ue=K.matrix,$e=ue.distance||Q.far;$e!==Q.far&&(Q.far=$e,Q.updateProjectionMatrix()),yo.setFromMatrixPosition(ue.matrixWorld),Q.position.copy(yo),ef.copy(Q.position),ef.add(Jw[k]),Q.up.copy(eT[k]),Q.lookAt(ef),Q.updateMatrixWorld(),Ue.makeTranslation(-yo.x,-yo.y,-yo.z),Kg.multiplyMatrices(Q.projectionMatrix,Q.matrixWorldInverse),K._frustum.setFromProjectionMatrix(Kg,Q.coordinateSystem,Q.reversedDepth)}else K.updateMatrices(ue);r=K.getFrustum(),N(D,E,K.camera,ue,this.type)}K.isPointLightShadow!==!0&&this.type===So&&P(K,E),K.needsUpdate=!1}y=this.type,v.needsUpdate=!1,s.setRenderTarget(I,z,B)};function P(R,D){const E=e.update(A);x.defines.VSM_SAMPLES!==R.blurSamples&&(x.defines.VSM_SAMPLES=R.blurSamples,M.defines.VSM_SAMPLES=R.blurSamples,x.needsUpdate=!0,M.needsUpdate=!0),R.mapPass===null&&(R.mapPass=new Vi(o.x,o.y,{format:bs,type:ur})),x.uniforms.shadow_pass.value=R.map.depthTexture,x.uniforms.resolution.value=R.mapSize,x.uniforms.radius.value=R.radius,s.setRenderTarget(R.mapPass),s.clear(),s.renderBufferDirect(D,null,E,x,A,null),M.uniforms.shadow_pass.value=R.mapPass.texture,M.uniforms.resolution.value=R.mapSize,M.uniforms.radius.value=R.radius,s.setRenderTarget(R.map),s.clear(),s.renderBufferDirect(D,null,E,M,A,null)}function U(R,D,E,I){let z=null;const B=E.isPointLight===!0?R.customDistanceMaterial:R.customDepthMaterial;if(B!==void 0)z=B;else if(z=E.isPointLight===!0?p:f,s.localClippingEnabled&&D.clipShadows===!0&&Array.isArray(D.clippingPlanes)&&D.clippingPlanes.length!==0||D.displacementMap&&D.displacementScale!==0||D.alphaMap&&D.alphaTest>0||D.map&&D.alphaTest>0||D.alphaToCoverage===!0){const H=z.uuid,ce=D.uuid;let he=m[H];he===void 0&&(he={},m[H]=he);let Z=he[ce];Z===void 0&&(Z=z.clone(),he[ce]=Z,D.addEventListener("dispose",L)),z=Z}if(z.visible=D.visible,z.wireframe=D.wireframe,I===So?z.side=D.shadowSide!==null?D.shadowSide:D.side:z.side=D.shadowSide!==null?D.shadowSide:S[D.side],z.alphaMap=D.alphaMap,z.alphaTest=D.alphaToCoverage===!0?.5:D.alphaTest,z.map=D.map,z.clipShadows=D.clipShadows,z.clippingPlanes=D.clippingPlanes,z.clipIntersection=D.clipIntersection,z.displacementMap=D.displacementMap,z.displacementScale=D.displacementScale,z.displacementBias=D.displacementBias,z.wireframeLinewidth=D.wireframeLinewidth,z.linewidth=D.linewidth,E.isPointLight===!0&&z.isMeshDistanceMaterial===!0){const H=s.properties.get(z);H.light=E}return z}function N(R,D,E,I,z){if(R.visible===!1)return;if(R.layers.test(D.layers)&&(R.isMesh||R.isLine||R.isPoints)&&(R.castShadow||R.receiveShadow&&z===So)&&(!R.frustumCulled||r.intersectsObject(R))){R.modelViewMatrix.multiplyMatrices(E.matrixWorldInverse,R.matrixWorld);const ce=e.update(R),he=R.material;if(Array.isArray(he)){const Z=ce.groups;for(let ue=0,K=Z.length;ue<K;ue++){const q=Z[ue],se=he[q.materialIndex];if(se&&se.visible){const le=U(R,se,I,z);R.onBeforeShadow(s,R,D,E,ce,le,q),s.renderBufferDirect(E,null,ce,le,R,q),R.onAfterShadow(s,R,D,E,ce,le,q)}}}else if(he.visible){const Z=U(R,he,I,z);R.onBeforeShadow(s,R,D,E,ce,Z,null),s.renderBufferDirect(E,null,ce,Z,R,null),R.onAfterShadow(s,R,D,E,ce,Z,null)}}const H=R.children;for(let ce=0,he=H.length;ce<he;ce++)N(H[ce],D,E,I,z)}function L(R){R.target.removeEventListener("dispose",L);for(const E in m){const I=m[E],z=R.target.uuid;z in I&&(I[z].dispose(),delete I[z])}}}function nT(s,e){function t(){let j=!1;const Ae=new sn;let pe=null;const Re=new sn(0,0,0,0);return{setMask:function(Ie){pe!==Ie&&!j&&(s.colorMask(Ie,Ie,Ie,Ie),pe=Ie)},setLocked:function(Ie){j=Ie},setClear:function(Ie,ve,Ge,He,kt){kt===!0&&(Ie*=He,ve*=He,Ge*=He),Ae.set(Ie,ve,Ge,He),Re.equals(Ae)===!1&&(s.clearColor(Ie,ve,Ge,He),Re.copy(Ae))},reset:function(){j=!1,pe=null,Re.set(-1,0,0,0)}}}function r(){let j=!1,Ae=!1,pe=null,Re=null,Ie=null;return{setReversed:function(ve){if(Ae!==ve){const Ge=e.get("EXT_clip_control");ve?Ge.clipControlEXT(Ge.LOWER_LEFT_EXT,Ge.ZERO_TO_ONE_EXT):Ge.clipControlEXT(Ge.LOWER_LEFT_EXT,Ge.NEGATIVE_ONE_TO_ONE_EXT),Ae=ve;const He=Ie;Ie=null,this.setClear(He)}},getReversed:function(){return Ae},setTest:function(ve){ve?me(s.DEPTH_TEST):Fe(s.DEPTH_TEST)},setMask:function(ve){pe!==ve&&!j&&(s.depthMask(ve),pe=ve)},setFunc:function(ve){if(Ae&&(ve=LS[ve]),Re!==ve){switch(ve){case of:s.depthFunc(s.NEVER);break;case lf:s.depthFunc(s.ALWAYS);break;case cf:s.depthFunc(s.LESS);break;case ga:s.depthFunc(s.LEQUAL);break;case uf:s.depthFunc(s.EQUAL);break;case df:s.depthFunc(s.GEQUAL);break;case ff:s.depthFunc(s.GREATER);break;case hf:s.depthFunc(s.NOTEQUAL);break;default:s.depthFunc(s.LEQUAL)}Re=ve}},setLocked:function(ve){j=ve},setClear:function(ve){Ie!==ve&&(Ie=ve,Ae&&(ve=1-ve),s.clearDepth(ve))},reset:function(){j=!1,pe=null,Re=null,Ie=null,Ae=!1}}}function o(){let j=!1,Ae=null,pe=null,Re=null,Ie=null,ve=null,Ge=null,He=null,kt=null;return{setTest:function(Rt){j||(Rt?me(s.STENCIL_TEST):Fe(s.STENCIL_TEST))},setMask:function(Rt){Ae!==Rt&&!j&&(s.stencilMask(Rt),Ae=Rt)},setFunc:function(Rt,Tn,ri){(pe!==Rt||Re!==Tn||Ie!==ri)&&(s.stencilFunc(Rt,Tn,ri),pe=Rt,Re=Tn,Ie=ri)},setOp:function(Rt,Tn,ri){(ve!==Rt||Ge!==Tn||He!==ri)&&(s.stencilOp(Rt,Tn,ri),ve=Rt,Ge=Tn,He=ri)},setLocked:function(Rt){j=Rt},setClear:function(Rt){kt!==Rt&&(s.clearStencil(Rt),kt=Rt)},reset:function(){j=!1,Ae=null,pe=null,Re=null,Ie=null,ve=null,Ge=null,He=null,kt=null}}}const l=new t,d=new r,f=new o,p=new WeakMap,m=new WeakMap;let _={},S={},x={},M=new WeakMap,w=[],A=null,v=!1,y=null,P=null,U=null,N=null,L=null,R=null,D=null,E=new Ct(0,0,0),I=0,z=!1,B=null,H=null,ce=null,he=null,Z=null;const ue=s.getParameter(s.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let K=!1,q=0;const se=s.getParameter(s.VERSION);se.indexOf("WebGL")!==-1?(q=parseFloat(/^WebGL (\d)/.exec(se)[1]),K=q>=1):se.indexOf("OpenGL ES")!==-1&&(q=parseFloat(/^OpenGL ES (\d)/.exec(se)[1]),K=q>=2);let le=null,k={};const Q=s.getParameter(s.SCISSOR_BOX),Ue=s.getParameter(s.VIEWPORT),$e=new sn().fromArray(Q),Ve=new sn().fromArray(Ue);function re(j,Ae,pe,Re){const Ie=new Uint8Array(4),ve=s.createTexture();s.bindTexture(j,ve),s.texParameteri(j,s.TEXTURE_MIN_FILTER,s.NEAREST),s.texParameteri(j,s.TEXTURE_MAG_FILTER,s.NEAREST);for(let Ge=0;Ge<pe;Ge++)j===s.TEXTURE_3D||j===s.TEXTURE_2D_ARRAY?s.texImage3D(Ae,0,s.RGBA,1,1,Re,0,s.RGBA,s.UNSIGNED_BYTE,Ie):s.texImage2D(Ae+Ge,0,s.RGBA,1,1,0,s.RGBA,s.UNSIGNED_BYTE,Ie);return ve}const _e={};_e[s.TEXTURE_2D]=re(s.TEXTURE_2D,s.TEXTURE_2D,1),_e[s.TEXTURE_CUBE_MAP]=re(s.TEXTURE_CUBE_MAP,s.TEXTURE_CUBE_MAP_POSITIVE_X,6),_e[s.TEXTURE_2D_ARRAY]=re(s.TEXTURE_2D_ARRAY,s.TEXTURE_2D_ARRAY,1,1),_e[s.TEXTURE_3D]=re(s.TEXTURE_3D,s.TEXTURE_3D,1,1),l.setClear(0,0,0,1),d.setClear(1),f.setClear(0),me(s.DEPTH_TEST),d.setFunc(ga),Xt(!1),tn($m),me(s.CULL_FACE),Mt(or);function me(j){_[j]!==!0&&(s.enable(j),_[j]=!0)}function Fe(j){_[j]!==!1&&(s.disable(j),_[j]=!1)}function Je(j,Ae){return x[j]!==Ae?(s.bindFramebuffer(j,Ae),x[j]=Ae,j===s.DRAW_FRAMEBUFFER&&(x[s.FRAMEBUFFER]=Ae),j===s.FRAMEBUFFER&&(x[s.DRAW_FRAMEBUFFER]=Ae),!0):!1}function et(j,Ae){let pe=w,Re=!1;if(j){pe=M.get(Ae),pe===void 0&&(pe=[],M.set(Ae,pe));const Ie=j.textures;if(pe.length!==Ie.length||pe[0]!==s.COLOR_ATTACHMENT0){for(let ve=0,Ge=Ie.length;ve<Ge;ve++)pe[ve]=s.COLOR_ATTACHMENT0+ve;pe.length=Ie.length,Re=!0}}else pe[0]!==s.BACK&&(pe[0]=s.BACK,Re=!0);Re&&s.drawBuffers(pe)}function Wt(j){return A!==j?(s.useProgram(j),A=j,!0):!1}const ft={[vs]:s.FUNC_ADD,[tS]:s.FUNC_SUBTRACT,[nS]:s.FUNC_REVERSE_SUBTRACT};ft[iS]=s.MIN,ft[rS]=s.MAX;const Nt={[sS]:s.ZERO,[aS]:s.ONE,[oS]:s.SRC_COLOR,[sf]:s.SRC_ALPHA,[hS]:s.SRC_ALPHA_SATURATE,[dS]:s.DST_COLOR,[cS]:s.DST_ALPHA,[lS]:s.ONE_MINUS_SRC_COLOR,[af]:s.ONE_MINUS_SRC_ALPHA,[fS]:s.ONE_MINUS_DST_COLOR,[uS]:s.ONE_MINUS_DST_ALPHA,[pS]:s.CONSTANT_COLOR,[mS]:s.ONE_MINUS_CONSTANT_COLOR,[gS]:s.CONSTANT_ALPHA,[xS]:s.ONE_MINUS_CONSTANT_ALPHA};function Mt(j,Ae,pe,Re,Ie,ve,Ge,He,kt,Rt){if(j===or){v===!0&&(Fe(s.BLEND),v=!1);return}if(v===!1&&(me(s.BLEND),v=!0),j!==eS){if(j!==y||Rt!==z){if((P!==vs||L!==vs)&&(s.blendEquation(s.FUNC_ADD),P=vs,L=vs),Rt)switch(j){case fa:s.blendFuncSeparate(s.ONE,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case Km:s.blendFunc(s.ONE,s.ONE);break;case Zm:s.blendFuncSeparate(s.ZERO,s.ONE_MINUS_SRC_COLOR,s.ZERO,s.ONE);break;case Qm:s.blendFuncSeparate(s.DST_COLOR,s.ONE_MINUS_SRC_ALPHA,s.ZERO,s.ONE);break;default:wt("WebGLState: Invalid blending: ",j);break}else switch(j){case fa:s.blendFuncSeparate(s.SRC_ALPHA,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case Km:s.blendFuncSeparate(s.SRC_ALPHA,s.ONE,s.ONE,s.ONE);break;case Zm:wt("WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true");break;case Qm:wt("WebGLState: MultiplyBlending requires material.premultipliedAlpha = true");break;default:wt("WebGLState: Invalid blending: ",j);break}U=null,N=null,R=null,D=null,E.set(0,0,0),I=0,y=j,z=Rt}return}Ie=Ie||Ae,ve=ve||pe,Ge=Ge||Re,(Ae!==P||Ie!==L)&&(s.blendEquationSeparate(ft[Ae],ft[Ie]),P=Ae,L=Ie),(pe!==U||Re!==N||ve!==R||Ge!==D)&&(s.blendFuncSeparate(Nt[pe],Nt[Re],Nt[ve],Nt[Ge]),U=pe,N=Re,R=ve,D=Ge),(He.equals(E)===!1||kt!==I)&&(s.blendColor(He.r,He.g,He.b,kt),E.copy(He),I=kt),y=j,z=!1}function _t(j,Ae){j.side===sr?Fe(s.CULL_FACE):me(s.CULL_FACE);let pe=j.side===Zn;Ae&&(pe=!pe),Xt(pe),j.blending===fa&&j.transparent===!1?Mt(or):Mt(j.blending,j.blendEquation,j.blendSrc,j.blendDst,j.blendEquationAlpha,j.blendSrcAlpha,j.blendDstAlpha,j.blendColor,j.blendAlpha,j.premultipliedAlpha),d.setFunc(j.depthFunc),d.setTest(j.depthTest),d.setMask(j.depthWrite),l.setMask(j.colorWrite);const Re=j.stencilWrite;f.setTest(Re),Re&&(f.setMask(j.stencilWriteMask),f.setFunc(j.stencilFunc,j.stencilRef,j.stencilFuncMask),f.setOp(j.stencilFail,j.stencilZFail,j.stencilZPass)),Kt(j.polygonOffset,j.polygonOffsetFactor,j.polygonOffsetUnits),j.alphaToCoverage===!0?me(s.SAMPLE_ALPHA_TO_COVERAGE):Fe(s.SAMPLE_ALPHA_TO_COVERAGE)}function Xt(j){B!==j&&(j?s.frontFace(s.CW):s.frontFace(s.CCW),B=j)}function tn(j){j!==Zy?(me(s.CULL_FACE),j!==H&&(j===$m?s.cullFace(s.BACK):j===Qy?s.cullFace(s.FRONT):s.cullFace(s.FRONT_AND_BACK))):Fe(s.CULL_FACE),H=j}function nn(j){j!==ce&&(K&&s.lineWidth(j),ce=j)}function Kt(j,Ae,pe){j?(me(s.POLYGON_OFFSET_FILL),(he!==Ae||Z!==pe)&&(he=Ae,Z=pe,d.getReversed()&&(Ae=-Ae),s.polygonOffset(Ae,pe))):Fe(s.POLYGON_OFFSET_FILL)}function It(j){j?me(s.SCISSOR_TEST):Fe(s.SCISSOR_TEST)}function qt(j){j===void 0&&(j=s.TEXTURE0+ue-1),le!==j&&(s.activeTexture(j),le=j)}function W(j,Ae,pe){pe===void 0&&(le===null?pe=s.TEXTURE0+ue-1:pe=le);let Re=k[pe];Re===void 0&&(Re={type:void 0,texture:void 0},k[pe]=Re),(Re.type!==j||Re.texture!==Ae)&&(le!==pe&&(s.activeTexture(pe),le=pe),s.bindTexture(j,Ae||_e[j]),Re.type=j,Re.texture=Ae)}function _n(){const j=k[le];j!==void 0&&j.type!==void 0&&(s.bindTexture(j.type,null),j.type=void 0,j.texture=void 0)}function Tt(){try{s.compressedTexImage2D(...arguments)}catch(j){wt("WebGLState:",j)}}function F(){try{s.compressedTexImage3D(...arguments)}catch(j){wt("WebGLState:",j)}}function b(){try{s.texSubImage2D(...arguments)}catch(j){wt("WebGLState:",j)}}function $(){try{s.texSubImage3D(...arguments)}catch(j){wt("WebGLState:",j)}}function ie(){try{s.compressedTexSubImage2D(...arguments)}catch(j){wt("WebGLState:",j)}}function de(){try{s.compressedTexSubImage3D(...arguments)}catch(j){wt("WebGLState:",j)}}function be(){try{s.texStorage2D(...arguments)}catch(j){wt("WebGLState:",j)}}function Ne(){try{s.texStorage3D(...arguments)}catch(j){wt("WebGLState:",j)}}function fe(){try{s.texImage2D(...arguments)}catch(j){wt("WebGLState:",j)}}function ge(){try{s.texImage3D(...arguments)}catch(j){wt("WebGLState:",j)}}function Pe(j){return S[j]!==void 0?S[j]:s.getParameter(j)}function qe(j,Ae){S[j]!==Ae&&(s.pixelStorei(j,Ae),S[j]=Ae)}function Le(j){$e.equals(j)===!1&&(s.scissor(j.x,j.y,j.z,j.w),$e.copy(j))}function Ce(j){Ve.equals(j)===!1&&(s.viewport(j.x,j.y,j.z,j.w),Ve.copy(j))}function Qe(j,Ae){let pe=m.get(Ae);pe===void 0&&(pe=new WeakMap,m.set(Ae,pe));let Re=pe.get(j);Re===void 0&&(Re=s.getUniformBlockIndex(Ae,j.name),pe.set(j,Re))}function tt(j,Ae){const Re=m.get(Ae).get(j);p.get(Ae)!==Re&&(s.uniformBlockBinding(Ae,Re,j.__bindingPointIndex),p.set(Ae,Re))}function at(){s.disable(s.BLEND),s.disable(s.CULL_FACE),s.disable(s.DEPTH_TEST),s.disable(s.POLYGON_OFFSET_FILL),s.disable(s.SCISSOR_TEST),s.disable(s.STENCIL_TEST),s.disable(s.SAMPLE_ALPHA_TO_COVERAGE),s.blendEquation(s.FUNC_ADD),s.blendFunc(s.ONE,s.ZERO),s.blendFuncSeparate(s.ONE,s.ZERO,s.ONE,s.ZERO),s.blendColor(0,0,0,0),s.colorMask(!0,!0,!0,!0),s.clearColor(0,0,0,0),s.depthMask(!0),s.depthFunc(s.LESS),d.setReversed(!1),s.clearDepth(1),s.stencilMask(4294967295),s.stencilFunc(s.ALWAYS,0,4294967295),s.stencilOp(s.KEEP,s.KEEP,s.KEEP),s.clearStencil(0),s.cullFace(s.BACK),s.frontFace(s.CCW),s.polygonOffset(0,0),s.activeTexture(s.TEXTURE0),s.bindFramebuffer(s.FRAMEBUFFER,null),s.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),s.bindFramebuffer(s.READ_FRAMEBUFFER,null),s.useProgram(null),s.lineWidth(1),s.scissor(0,0,s.canvas.width,s.canvas.height),s.viewport(0,0,s.canvas.width,s.canvas.height),s.pixelStorei(s.PACK_ALIGNMENT,4),s.pixelStorei(s.UNPACK_ALIGNMENT,4),s.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,!1),s.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,!1),s.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,s.BROWSER_DEFAULT_WEBGL),s.pixelStorei(s.PACK_ROW_LENGTH,0),s.pixelStorei(s.PACK_SKIP_PIXELS,0),s.pixelStorei(s.PACK_SKIP_ROWS,0),s.pixelStorei(s.UNPACK_ROW_LENGTH,0),s.pixelStorei(s.UNPACK_IMAGE_HEIGHT,0),s.pixelStorei(s.UNPACK_SKIP_PIXELS,0),s.pixelStorei(s.UNPACK_SKIP_ROWS,0),s.pixelStorei(s.UNPACK_SKIP_IMAGES,0),_={},S={},le=null,k={},x={},M=new WeakMap,w=[],A=null,v=!1,y=null,P=null,U=null,N=null,L=null,R=null,D=null,E=new Ct(0,0,0),I=0,z=!1,B=null,H=null,ce=null,he=null,Z=null,$e.set(0,0,s.canvas.width,s.canvas.height),Ve.set(0,0,s.canvas.width,s.canvas.height),l.reset(),d.reset(),f.reset()}return{buffers:{color:l,depth:d,stencil:f},enable:me,disable:Fe,bindFramebuffer:Je,drawBuffers:et,useProgram:Wt,setBlending:Mt,setMaterial:_t,setFlipSided:Xt,setCullFace:tn,setLineWidth:nn,setPolygonOffset:Kt,setScissorTest:It,activeTexture:qt,bindTexture:W,unbindTexture:_n,compressedTexImage2D:Tt,compressedTexImage3D:F,texImage2D:fe,texImage3D:ge,pixelStorei:qe,getParameter:Pe,updateUBOMapping:Qe,uniformBlockBinding:tt,texStorage2D:be,texStorage3D:Ne,texSubImage2D:b,texSubImage3D:$,compressedTexSubImage2D:ie,compressedTexSubImage3D:de,scissor:Le,viewport:Ce,reset:at}}function iT(s,e,t,r,o,l,d){const f=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,p=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),m=new yt,_=new WeakMap,S=new Set;let x;const M=new WeakMap;let w=!1;try{w=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function A(F,b){return w?new OffscreenCanvas(F,b):Ec("canvas")}function v(F,b,$){let ie=1;const de=Tt(F);if((de.width>$||de.height>$)&&(ie=$/Math.max(de.width,de.height)),ie<1)if(typeof HTMLImageElement<"u"&&F instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&F instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&F instanceof ImageBitmap||typeof VideoFrame<"u"&&F instanceof VideoFrame){const be=Math.floor(ie*de.width),Ne=Math.floor(ie*de.height);x===void 0&&(x=A(be,Ne));const fe=b?A(be,Ne):x;return fe.width=be,fe.height=Ne,fe.getContext("2d").drawImage(F,0,0,be,Ne),rt("WebGLRenderer: Texture has been resized from ("+de.width+"x"+de.height+") to ("+be+"x"+Ne+")."),fe}else return"data"in F&&rt("WebGLRenderer: Image in DataTexture is too big ("+de.width+"x"+de.height+")."),F;return F}function y(F){return F.generateMipmaps}function P(F){s.generateMipmap(F)}function U(F){return F.isWebGLCubeRenderTarget?s.TEXTURE_CUBE_MAP:F.isWebGL3DRenderTarget?s.TEXTURE_3D:F.isWebGLArrayRenderTarget||F.isCompressedArrayTexture?s.TEXTURE_2D_ARRAY:s.TEXTURE_2D}function N(F,b,$,ie,de,be=!1){if(F!==null){if(s[F]!==void 0)return s[F];rt("WebGLRenderer: Attempt to use non-existing WebGL internal format '"+F+"'")}let Ne;ie&&(Ne=e.get("EXT_texture_norm16"),Ne||rt("WebGLRenderer: Unable to use normalized textures without EXT_texture_norm16 extension"));let fe=b;if(b===s.RED&&($===s.FLOAT&&(fe=s.R32F),$===s.HALF_FLOAT&&(fe=s.R16F),$===s.UNSIGNED_BYTE&&(fe=s.R8),$===s.UNSIGNED_SHORT&&Ne&&(fe=Ne.R16_EXT),$===s.SHORT&&Ne&&(fe=Ne.R16_SNORM_EXT)),b===s.RED_INTEGER&&($===s.UNSIGNED_BYTE&&(fe=s.R8UI),$===s.UNSIGNED_SHORT&&(fe=s.R16UI),$===s.UNSIGNED_INT&&(fe=s.R32UI),$===s.BYTE&&(fe=s.R8I),$===s.SHORT&&(fe=s.R16I),$===s.INT&&(fe=s.R32I)),b===s.RG&&($===s.FLOAT&&(fe=s.RG32F),$===s.HALF_FLOAT&&(fe=s.RG16F),$===s.UNSIGNED_BYTE&&(fe=s.RG8),$===s.UNSIGNED_SHORT&&Ne&&(fe=Ne.RG16_EXT),$===s.SHORT&&Ne&&(fe=Ne.RG16_SNORM_EXT)),b===s.RG_INTEGER&&($===s.UNSIGNED_BYTE&&(fe=s.RG8UI),$===s.UNSIGNED_SHORT&&(fe=s.RG16UI),$===s.UNSIGNED_INT&&(fe=s.RG32UI),$===s.BYTE&&(fe=s.RG8I),$===s.SHORT&&(fe=s.RG16I),$===s.INT&&(fe=s.RG32I)),b===s.RGB_INTEGER&&($===s.UNSIGNED_BYTE&&(fe=s.RGB8UI),$===s.UNSIGNED_SHORT&&(fe=s.RGB16UI),$===s.UNSIGNED_INT&&(fe=s.RGB32UI),$===s.BYTE&&(fe=s.RGB8I),$===s.SHORT&&(fe=s.RGB16I),$===s.INT&&(fe=s.RGB32I)),b===s.RGBA_INTEGER&&($===s.UNSIGNED_BYTE&&(fe=s.RGBA8UI),$===s.UNSIGNED_SHORT&&(fe=s.RGBA16UI),$===s.UNSIGNED_INT&&(fe=s.RGBA32UI),$===s.BYTE&&(fe=s.RGBA8I),$===s.SHORT&&(fe=s.RGBA16I),$===s.INT&&(fe=s.RGBA32I)),b===s.RGB&&($===s.UNSIGNED_SHORT&&Ne&&(fe=Ne.RGB16_EXT),$===s.SHORT&&Ne&&(fe=Ne.RGB16_SNORM_EXT),$===s.UNSIGNED_INT_5_9_9_9_REV&&(fe=s.RGB9_E5),$===s.UNSIGNED_INT_10F_11F_11F_REV&&(fe=s.R11F_G11F_B10F)),b===s.RGBA){const ge=be?Mc:St.getTransfer(de);$===s.FLOAT&&(fe=s.RGBA32F),$===s.HALF_FLOAT&&(fe=s.RGBA16F),$===s.UNSIGNED_BYTE&&(fe=ge===Ft?s.SRGB8_ALPHA8:s.RGBA8),$===s.UNSIGNED_SHORT&&Ne&&(fe=Ne.RGBA16_EXT),$===s.SHORT&&Ne&&(fe=Ne.RGBA16_SNORM_EXT),$===s.UNSIGNED_SHORT_4_4_4_4&&(fe=s.RGBA4),$===s.UNSIGNED_SHORT_5_5_5_1&&(fe=s.RGB5_A1)}return(fe===s.R16F||fe===s.R32F||fe===s.RG16F||fe===s.RG32F||fe===s.RGBA16F||fe===s.RGBA32F)&&e.get("EXT_color_buffer_float"),fe}function L(F,b){let $;return F?b===null||b===Hi||b===To?$=s.DEPTH24_STENCIL8:b===Oi?$=s.DEPTH32F_STENCIL8:b===wo&&($=s.DEPTH24_STENCIL8,rt("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):b===null||b===Hi||b===To?$=s.DEPTH_COMPONENT24:b===Oi?$=s.DEPTH_COMPONENT32F:b===wo&&($=s.DEPTH_COMPONENT16),$}function R(F,b){return y(F)===!0||F.isFramebufferTexture&&F.minFilter!==wn&&F.minFilter!==In?Math.log2(Math.max(b.width,b.height))+1:F.mipmaps!==void 0&&F.mipmaps.length>0?F.mipmaps.length:F.isCompressedTexture&&Array.isArray(F.image)?b.mipmaps.length:1}function D(F){const b=F.target;b.removeEventListener("dispose",D),I(b),b.isVideoTexture&&_.delete(b),b.isHTMLTexture&&S.delete(b)}function E(F){const b=F.target;b.removeEventListener("dispose",E),B(b)}function I(F){const b=r.get(F);if(b.__webglInit===void 0)return;const $=F.source,ie=M.get($);if(ie){const de=ie[b.__cacheKey];de.usedTimes--,de.usedTimes===0&&z(F),Object.keys(ie).length===0&&M.delete($)}r.remove(F)}function z(F){const b=r.get(F);s.deleteTexture(b.__webglTexture);const $=F.source,ie=M.get($);delete ie[b.__cacheKey],d.memory.textures--}function B(F){const b=r.get(F);if(F.depthTexture&&(F.depthTexture.dispose(),r.remove(F.depthTexture)),F.isWebGLCubeRenderTarget)for(let ie=0;ie<6;ie++){if(Array.isArray(b.__webglFramebuffer[ie]))for(let de=0;de<b.__webglFramebuffer[ie].length;de++)s.deleteFramebuffer(b.__webglFramebuffer[ie][de]);else s.deleteFramebuffer(b.__webglFramebuffer[ie]);b.__webglDepthbuffer&&s.deleteRenderbuffer(b.__webglDepthbuffer[ie])}else{if(Array.isArray(b.__webglFramebuffer))for(let ie=0;ie<b.__webglFramebuffer.length;ie++)s.deleteFramebuffer(b.__webglFramebuffer[ie]);else s.deleteFramebuffer(b.__webglFramebuffer);if(b.__webglDepthbuffer&&s.deleteRenderbuffer(b.__webglDepthbuffer),b.__webglMultisampledFramebuffer&&s.deleteFramebuffer(b.__webglMultisampledFramebuffer),b.__webglColorRenderbuffer)for(let ie=0;ie<b.__webglColorRenderbuffer.length;ie++)b.__webglColorRenderbuffer[ie]&&s.deleteRenderbuffer(b.__webglColorRenderbuffer[ie]);b.__webglDepthRenderbuffer&&s.deleteRenderbuffer(b.__webglDepthRenderbuffer)}const $=F.textures;for(let ie=0,de=$.length;ie<de;ie++){const be=r.get($[ie]);be.__webglTexture&&(s.deleteTexture(be.__webglTexture),d.memory.textures--),r.remove($[ie])}r.remove(F)}let H=0;function ce(){H=0}function he(){return H}function Z(F){H=F}function ue(){const F=H;return F>=o.maxTextures&&rt("WebGLTextures: Trying to use "+F+" texture units while this GPU supports only "+o.maxTextures),H+=1,F}function K(F){const b=[];return b.push(F.wrapS),b.push(F.wrapT),b.push(F.wrapR||0),b.push(F.magFilter),b.push(F.minFilter),b.push(F.anisotropy),b.push(F.internalFormat),b.push(F.format),b.push(F.type),b.push(F.generateMipmaps),b.push(F.premultiplyAlpha),b.push(F.flipY),b.push(F.unpackAlignment),b.push(F.colorSpace),b.join()}function q(F,b){const $=r.get(F);if(F.isVideoTexture&&W(F),F.isRenderTargetTexture===!1&&F.isExternalTexture!==!0&&F.version>0&&$.__version!==F.version){const ie=F.image;if(ie===null)rt("WebGLRenderer: Texture marked for update but no image data found.");else if(ie.complete===!1)rt("WebGLRenderer: Texture marked for update but image is incomplete");else{Fe($,F,b);return}}else F.isExternalTexture&&($.__webglTexture=F.sourceTexture?F.sourceTexture:null);t.bindTexture(s.TEXTURE_2D,$.__webglTexture,s.TEXTURE0+b)}function se(F,b){const $=r.get(F);if(F.isRenderTargetTexture===!1&&F.version>0&&$.__version!==F.version){Fe($,F,b);return}else F.isExternalTexture&&($.__webglTexture=F.sourceTexture?F.sourceTexture:null);t.bindTexture(s.TEXTURE_2D_ARRAY,$.__webglTexture,s.TEXTURE0+b)}function le(F,b){const $=r.get(F);if(F.isRenderTargetTexture===!1&&F.version>0&&$.__version!==F.version){Fe($,F,b);return}t.bindTexture(s.TEXTURE_3D,$.__webglTexture,s.TEXTURE0+b)}function k(F,b){const $=r.get(F);if(F.isCubeDepthTexture!==!0&&F.version>0&&$.__version!==F.version){Je($,F,b);return}t.bindTexture(s.TEXTURE_CUBE_MAP,$.__webglTexture,s.TEXTURE0+b)}const Q={[pf]:s.REPEAT,[ar]:s.CLAMP_TO_EDGE,[mf]:s.MIRRORED_REPEAT},Ue={[wn]:s.NEAREST,[yS]:s.NEAREST_MIPMAP_NEAREST,[Ol]:s.NEAREST_MIPMAP_LINEAR,[In]:s.LINEAR,[bd]:s.LINEAR_MIPMAP_NEAREST,[ys]:s.LINEAR_MIPMAP_LINEAR},$e={[bS]:s.NEVER,[CS]:s.ALWAYS,[ES]:s.LESS,[ch]:s.LEQUAL,[wS]:s.EQUAL,[uh]:s.GEQUAL,[TS]:s.GREATER,[AS]:s.NOTEQUAL};function Ve(F,b){if(b.type===Oi&&e.has("OES_texture_float_linear")===!1&&(b.magFilter===In||b.magFilter===bd||b.magFilter===Ol||b.magFilter===ys||b.minFilter===In||b.minFilter===bd||b.minFilter===Ol||b.minFilter===ys)&&rt("WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),s.texParameteri(F,s.TEXTURE_WRAP_S,Q[b.wrapS]),s.texParameteri(F,s.TEXTURE_WRAP_T,Q[b.wrapT]),(F===s.TEXTURE_3D||F===s.TEXTURE_2D_ARRAY)&&s.texParameteri(F,s.TEXTURE_WRAP_R,Q[b.wrapR]),s.texParameteri(F,s.TEXTURE_MAG_FILTER,Ue[b.magFilter]),s.texParameteri(F,s.TEXTURE_MIN_FILTER,Ue[b.minFilter]),b.compareFunction&&(s.texParameteri(F,s.TEXTURE_COMPARE_MODE,s.COMPARE_REF_TO_TEXTURE),s.texParameteri(F,s.TEXTURE_COMPARE_FUNC,$e[b.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(b.magFilter===wn||b.minFilter!==Ol&&b.minFilter!==ys||b.type===Oi&&e.has("OES_texture_float_linear")===!1)return;if(b.anisotropy>1||r.get(b).__currentAnisotropy){const $=e.get("EXT_texture_filter_anisotropic");s.texParameterf(F,$.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(b.anisotropy,o.getMaxAnisotropy())),r.get(b).__currentAnisotropy=b.anisotropy}}}function re(F,b){let $=!1;F.__webglInit===void 0&&(F.__webglInit=!0,b.addEventListener("dispose",D));const ie=b.source;let de=M.get(ie);de===void 0&&(de={},M.set(ie,de));const be=K(b);if(be!==F.__cacheKey){de[be]===void 0&&(de[be]={texture:s.createTexture(),usedTimes:0},d.memory.textures++,$=!0),de[be].usedTimes++;const Ne=de[F.__cacheKey];Ne!==void 0&&(de[F.__cacheKey].usedTimes--,Ne.usedTimes===0&&z(b)),F.__cacheKey=be,F.__webglTexture=de[be].texture}return $}function _e(F,b,$){return Math.floor(Math.floor(F/$)/b)}function me(F,b,$,ie){const be=F.updateRanges;if(be.length===0)t.texSubImage2D(s.TEXTURE_2D,0,0,0,b.width,b.height,$,ie,b.data);else{be.sort((qe,Le)=>qe.start-Le.start);let Ne=0;for(let qe=1;qe<be.length;qe++){const Le=be[Ne],Ce=be[qe],Qe=Le.start+Le.count,tt=_e(Ce.start,b.width,4),at=_e(Le.start,b.width,4);Ce.start<=Qe+1&&tt===at&&_e(Ce.start+Ce.count-1,b.width,4)===tt?Le.count=Math.max(Le.count,Ce.start+Ce.count-Le.start):(++Ne,be[Ne]=Ce)}be.length=Ne+1;const fe=t.getParameter(s.UNPACK_ROW_LENGTH),ge=t.getParameter(s.UNPACK_SKIP_PIXELS),Pe=t.getParameter(s.UNPACK_SKIP_ROWS);t.pixelStorei(s.UNPACK_ROW_LENGTH,b.width);for(let qe=0,Le=be.length;qe<Le;qe++){const Ce=be[qe],Qe=Math.floor(Ce.start/4),tt=Math.ceil(Ce.count/4),at=Qe%b.width,j=Math.floor(Qe/b.width),Ae=tt,pe=1;t.pixelStorei(s.UNPACK_SKIP_PIXELS,at),t.pixelStorei(s.UNPACK_SKIP_ROWS,j),t.texSubImage2D(s.TEXTURE_2D,0,at,j,Ae,pe,$,ie,b.data)}F.clearUpdateRanges(),t.pixelStorei(s.UNPACK_ROW_LENGTH,fe),t.pixelStorei(s.UNPACK_SKIP_PIXELS,ge),t.pixelStorei(s.UNPACK_SKIP_ROWS,Pe)}}function Fe(F,b,$){let ie=s.TEXTURE_2D;(b.isDataArrayTexture||b.isCompressedArrayTexture)&&(ie=s.TEXTURE_2D_ARRAY),b.isData3DTexture&&(ie=s.TEXTURE_3D);const de=re(F,b),be=b.source;t.bindTexture(ie,F.__webglTexture,s.TEXTURE0+$);const Ne=r.get(be);if(be.version!==Ne.__version||de===!0){if(t.activeTexture(s.TEXTURE0+$),(typeof ImageBitmap<"u"&&b.image instanceof ImageBitmap)===!1){const pe=St.getPrimaries(St.workingColorSpace),Re=b.colorSpace===jr?null:St.getPrimaries(b.colorSpace),Ie=b.colorSpace===jr||pe===Re?s.NONE:s.BROWSER_DEFAULT_WEBGL;t.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,b.flipY),t.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,b.premultiplyAlpha),t.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,Ie)}t.pixelStorei(s.UNPACK_ALIGNMENT,b.unpackAlignment);let ge=v(b.image,!1,o.maxTextureSize);ge=_n(b,ge);const Pe=l.convert(b.format,b.colorSpace),qe=l.convert(b.type);let Le=N(b.internalFormat,Pe,qe,b.normalized,b.colorSpace,b.isVideoTexture);Ve(ie,b);let Ce;const Qe=b.mipmaps,tt=b.isVideoTexture!==!0,at=Ne.__version===void 0||de===!0,j=be.dataReady,Ae=R(b,ge);if(b.isDepthTexture)Le=L(b.format===Ss,b.type),at&&(tt?t.texStorage2D(s.TEXTURE_2D,1,Le,ge.width,ge.height):t.texImage2D(s.TEXTURE_2D,0,Le,ge.width,ge.height,0,Pe,qe,null));else if(b.isDataTexture)if(Qe.length>0){tt&&at&&t.texStorage2D(s.TEXTURE_2D,Ae,Le,Qe[0].width,Qe[0].height);for(let pe=0,Re=Qe.length;pe<Re;pe++)Ce=Qe[pe],tt?j&&t.texSubImage2D(s.TEXTURE_2D,pe,0,0,Ce.width,Ce.height,Pe,qe,Ce.data):t.texImage2D(s.TEXTURE_2D,pe,Le,Ce.width,Ce.height,0,Pe,qe,Ce.data);b.generateMipmaps=!1}else tt?(at&&t.texStorage2D(s.TEXTURE_2D,Ae,Le,ge.width,ge.height),j&&me(b,ge,Pe,qe)):t.texImage2D(s.TEXTURE_2D,0,Le,ge.width,ge.height,0,Pe,qe,ge.data);else if(b.isCompressedTexture)if(b.isCompressedArrayTexture){tt&&at&&t.texStorage3D(s.TEXTURE_2D_ARRAY,Ae,Le,Qe[0].width,Qe[0].height,ge.depth);for(let pe=0,Re=Qe.length;pe<Re;pe++)if(Ce=Qe[pe],b.format!==Ci)if(Pe!==null)if(tt){if(j)if(b.layerUpdates.size>0){const Ie=Ag(Ce.width,Ce.height,b.format,b.type);for(const ve of b.layerUpdates){const Ge=Ce.data.subarray(ve*Ie/Ce.data.BYTES_PER_ELEMENT,(ve+1)*Ie/Ce.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,pe,0,0,ve,Ce.width,Ce.height,1,Pe,Ge)}b.clearLayerUpdates()}else t.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,pe,0,0,0,Ce.width,Ce.height,ge.depth,Pe,Ce.data)}else t.compressedTexImage3D(s.TEXTURE_2D_ARRAY,pe,Le,Ce.width,Ce.height,ge.depth,0,Ce.data,0,0);else rt("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else tt?j&&t.texSubImage3D(s.TEXTURE_2D_ARRAY,pe,0,0,0,Ce.width,Ce.height,ge.depth,Pe,qe,Ce.data):t.texImage3D(s.TEXTURE_2D_ARRAY,pe,Le,Ce.width,Ce.height,ge.depth,0,Pe,qe,Ce.data)}else{tt&&at&&t.texStorage2D(s.TEXTURE_2D,Ae,Le,Qe[0].width,Qe[0].height);for(let pe=0,Re=Qe.length;pe<Re;pe++)Ce=Qe[pe],b.format!==Ci?Pe!==null?tt?j&&t.compressedTexSubImage2D(s.TEXTURE_2D,pe,0,0,Ce.width,Ce.height,Pe,Ce.data):t.compressedTexImage2D(s.TEXTURE_2D,pe,Le,Ce.width,Ce.height,0,Ce.data):rt("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):tt?j&&t.texSubImage2D(s.TEXTURE_2D,pe,0,0,Ce.width,Ce.height,Pe,qe,Ce.data):t.texImage2D(s.TEXTURE_2D,pe,Le,Ce.width,Ce.height,0,Pe,qe,Ce.data)}else if(b.isDataArrayTexture)if(tt){if(at&&t.texStorage3D(s.TEXTURE_2D_ARRAY,Ae,Le,ge.width,ge.height,ge.depth),j)if(b.layerUpdates.size>0){const pe=Ag(ge.width,ge.height,b.format,b.type);for(const Re of b.layerUpdates){const Ie=ge.data.subarray(Re*pe/ge.data.BYTES_PER_ELEMENT,(Re+1)*pe/ge.data.BYTES_PER_ELEMENT);t.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,Re,ge.width,ge.height,1,Pe,qe,Ie)}b.clearLayerUpdates()}else t.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,0,ge.width,ge.height,ge.depth,Pe,qe,ge.data)}else t.texImage3D(s.TEXTURE_2D_ARRAY,0,Le,ge.width,ge.height,ge.depth,0,Pe,qe,ge.data);else if(b.isData3DTexture)tt?(at&&t.texStorage3D(s.TEXTURE_3D,Ae,Le,ge.width,ge.height,ge.depth),j&&t.texSubImage3D(s.TEXTURE_3D,0,0,0,0,ge.width,ge.height,ge.depth,Pe,qe,ge.data)):t.texImage3D(s.TEXTURE_3D,0,Le,ge.width,ge.height,ge.depth,0,Pe,qe,ge.data);else if(b.isFramebufferTexture){if(at)if(tt)t.texStorage2D(s.TEXTURE_2D,Ae,Le,ge.width,ge.height);else{let pe=ge.width,Re=ge.height;for(let Ie=0;Ie<Ae;Ie++)t.texImage2D(s.TEXTURE_2D,Ie,Le,pe,Re,0,Pe,qe,null),pe>>=1,Re>>=1}}else if(b.isHTMLTexture){if("texElementImage2D"in s){const pe=s.canvas;if(pe.hasAttribute("layoutsubtree")||pe.setAttribute("layoutsubtree","true"),ge.parentNode!==pe){pe.appendChild(ge),S.add(b),pe.onpaint=Re=>{const Ie=Re.changedElements;for(const ve of S)Ie.includes(ve.image)&&(ve.needsUpdate=!0)},pe.requestPaint();return}if(s.texElementImage2D.length===3)s.texElementImage2D(s.TEXTURE_2D,s.RGBA8,ge);else{const Ie=s.RGBA,ve=s.RGBA,Ge=s.UNSIGNED_BYTE;s.texElementImage2D(s.TEXTURE_2D,0,Ie,ve,Ge,ge)}s.texParameteri(s.TEXTURE_2D,s.TEXTURE_MIN_FILTER,s.LINEAR),s.texParameteri(s.TEXTURE_2D,s.TEXTURE_WRAP_S,s.CLAMP_TO_EDGE),s.texParameteri(s.TEXTURE_2D,s.TEXTURE_WRAP_T,s.CLAMP_TO_EDGE)}}else if(Qe.length>0){if(tt&&at){const pe=Tt(Qe[0]);t.texStorage2D(s.TEXTURE_2D,Ae,Le,pe.width,pe.height)}for(let pe=0,Re=Qe.length;pe<Re;pe++)Ce=Qe[pe],tt?j&&t.texSubImage2D(s.TEXTURE_2D,pe,0,0,Pe,qe,Ce):t.texImage2D(s.TEXTURE_2D,pe,Le,Pe,qe,Ce);b.generateMipmaps=!1}else if(tt){if(at){const pe=Tt(ge);t.texStorage2D(s.TEXTURE_2D,Ae,Le,pe.width,pe.height)}j&&t.texSubImage2D(s.TEXTURE_2D,0,0,0,Pe,qe,ge)}else t.texImage2D(s.TEXTURE_2D,0,Le,Pe,qe,ge);y(b)&&P(ie),Ne.__version=be.version,b.onUpdate&&b.onUpdate(b)}F.__version=b.version}function Je(F,b,$){if(b.image.length!==6)return;const ie=re(F,b),de=b.source;t.bindTexture(s.TEXTURE_CUBE_MAP,F.__webglTexture,s.TEXTURE0+$);const be=r.get(de);if(de.version!==be.__version||ie===!0){t.activeTexture(s.TEXTURE0+$);const Ne=St.getPrimaries(St.workingColorSpace),fe=b.colorSpace===jr?null:St.getPrimaries(b.colorSpace),ge=b.colorSpace===jr||Ne===fe?s.NONE:s.BROWSER_DEFAULT_WEBGL;t.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,b.flipY),t.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,b.premultiplyAlpha),t.pixelStorei(s.UNPACK_ALIGNMENT,b.unpackAlignment),t.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,ge);const Pe=b.isCompressedTexture||b.image[0].isCompressedTexture,qe=b.image[0]&&b.image[0].isDataTexture,Le=[];for(let ve=0;ve<6;ve++)!Pe&&!qe?Le[ve]=v(b.image[ve],!0,o.maxCubemapSize):Le[ve]=qe?b.image[ve].image:b.image[ve],Le[ve]=_n(b,Le[ve]);const Ce=Le[0],Qe=l.convert(b.format,b.colorSpace),tt=l.convert(b.type),at=N(b.internalFormat,Qe,tt,b.normalized,b.colorSpace),j=b.isVideoTexture!==!0,Ae=be.__version===void 0||ie===!0,pe=de.dataReady;let Re=R(b,Ce);Ve(s.TEXTURE_CUBE_MAP,b);let Ie;if(Pe){j&&Ae&&t.texStorage2D(s.TEXTURE_CUBE_MAP,Re,at,Ce.width,Ce.height);for(let ve=0;ve<6;ve++){Ie=Le[ve].mipmaps;for(let Ge=0;Ge<Ie.length;Ge++){const He=Ie[Ge];b.format!==Ci?Qe!==null?j?pe&&t.compressedTexSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge,0,0,He.width,He.height,Qe,He.data):t.compressedTexImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge,at,He.width,He.height,0,He.data):rt("WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):j?pe&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge,0,0,He.width,He.height,Qe,tt,He.data):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge,at,He.width,He.height,0,Qe,tt,He.data)}}}else{if(Ie=b.mipmaps,j&&Ae){Ie.length>0&&Re++;const ve=Tt(Le[0]);t.texStorage2D(s.TEXTURE_CUBE_MAP,Re,at,ve.width,ve.height)}for(let ve=0;ve<6;ve++)if(qe){j?pe&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,0,0,0,Le[ve].width,Le[ve].height,Qe,tt,Le[ve].data):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,0,at,Le[ve].width,Le[ve].height,0,Qe,tt,Le[ve].data);for(let Ge=0;Ge<Ie.length;Ge++){const kt=Ie[Ge].image[ve].image;j?pe&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge+1,0,0,kt.width,kt.height,Qe,tt,kt.data):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge+1,at,kt.width,kt.height,0,Qe,tt,kt.data)}}else{j?pe&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,0,0,0,Qe,tt,Le[ve]):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,0,at,Qe,tt,Le[ve]);for(let Ge=0;Ge<Ie.length;Ge++){const He=Ie[Ge];j?pe&&t.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge+1,0,0,Qe,tt,He.image[ve]):t.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+ve,Ge+1,at,Qe,tt,He.image[ve])}}}y(b)&&P(s.TEXTURE_CUBE_MAP),be.__version=de.version,b.onUpdate&&b.onUpdate(b)}F.__version=b.version}function et(F,b,$,ie,de,be){const Ne=l.convert($.format,$.colorSpace),fe=l.convert($.type),ge=N($.internalFormat,Ne,fe,$.normalized,$.colorSpace),Pe=r.get(b),qe=r.get($);if(qe.__renderTarget=b,!Pe.__hasExternalTextures){const Le=Math.max(1,b.width>>be),Ce=Math.max(1,b.height>>be);de===s.TEXTURE_3D||de===s.TEXTURE_2D_ARRAY?t.texImage3D(de,be,ge,Le,Ce,b.depth,0,Ne,fe,null):t.texImage2D(de,be,ge,Le,Ce,0,Ne,fe,null)}t.bindFramebuffer(s.FRAMEBUFFER,F),qt(b)?f.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,ie,de,qe.__webglTexture,0,It(b)):(de===s.TEXTURE_2D||de>=s.TEXTURE_CUBE_MAP_POSITIVE_X&&de<=s.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&s.framebufferTexture2D(s.FRAMEBUFFER,ie,de,qe.__webglTexture,be),t.bindFramebuffer(s.FRAMEBUFFER,null)}function Wt(F,b,$){if(s.bindRenderbuffer(s.RENDERBUFFER,F),b.depthBuffer){const ie=b.depthTexture,de=ie&&ie.isDepthTexture?ie.type:null,be=L(b.stencilBuffer,de),Ne=b.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;qt(b)?f.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,It(b),be,b.width,b.height):$?s.renderbufferStorageMultisample(s.RENDERBUFFER,It(b),be,b.width,b.height):s.renderbufferStorage(s.RENDERBUFFER,be,b.width,b.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,Ne,s.RENDERBUFFER,F)}else{const ie=b.textures;for(let de=0;de<ie.length;de++){const be=ie[de],Ne=l.convert(be.format,be.colorSpace),fe=l.convert(be.type),ge=N(be.internalFormat,Ne,fe,be.normalized,be.colorSpace);qt(b)?f.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,It(b),ge,b.width,b.height):$?s.renderbufferStorageMultisample(s.RENDERBUFFER,It(b),ge,b.width,b.height):s.renderbufferStorage(s.RENDERBUFFER,ge,b.width,b.height)}}s.bindRenderbuffer(s.RENDERBUFFER,null)}function ft(F,b,$){const ie=b.isWebGLCubeRenderTarget===!0;if(t.bindFramebuffer(s.FRAMEBUFFER,F),!(b.depthTexture&&b.depthTexture.isDepthTexture))throw new Error("THREE.WebGLTextures: renderTarget.depthTexture must be an instance of THREE.DepthTexture.");const de=r.get(b.depthTexture);if(de.__renderTarget=b,(!de.__webglTexture||b.depthTexture.image.width!==b.width||b.depthTexture.image.height!==b.height)&&(b.depthTexture.image.width=b.width,b.depthTexture.image.height=b.height,b.depthTexture.needsUpdate=!0),ie){if(de.__webglInit===void 0&&(de.__webglInit=!0,b.depthTexture.addEventListener("dispose",D)),de.__webglTexture===void 0){de.__webglTexture=s.createTexture(),t.bindTexture(s.TEXTURE_CUBE_MAP,de.__webglTexture),Ve(s.TEXTURE_CUBE_MAP,b.depthTexture);const Pe=l.convert(b.depthTexture.format),qe=l.convert(b.depthTexture.type);let Le;b.depthTexture.format===dr?Le=s.DEPTH_COMPONENT24:b.depthTexture.format===Ss&&(Le=s.DEPTH24_STENCIL8);for(let Ce=0;Ce<6;Ce++)s.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+Ce,0,Le,b.width,b.height,0,Pe,qe,null)}}else q(b.depthTexture,0);const be=de.__webglTexture,Ne=It(b),fe=ie?s.TEXTURE_CUBE_MAP_POSITIVE_X+$:s.TEXTURE_2D,ge=b.depthTexture.format===Ss?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;if(b.depthTexture.format===dr)qt(b)?f.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,ge,fe,be,0,Ne):s.framebufferTexture2D(s.FRAMEBUFFER,ge,fe,be,0);else if(b.depthTexture.format===Ss)qt(b)?f.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,ge,fe,be,0,Ne):s.framebufferTexture2D(s.FRAMEBUFFER,ge,fe,be,0);else throw new Error("THREE.WebGLTextures: Unknown depthTexture format.")}function Nt(F){const b=r.get(F),$=F.isWebGLCubeRenderTarget===!0;if(b.__boundDepthTexture!==F.depthTexture){const ie=F.depthTexture;if(b.__depthDisposeCallback&&b.__depthDisposeCallback(),ie){const de=()=>{delete b.__boundDepthTexture,delete b.__depthDisposeCallback,ie.removeEventListener("dispose",de)};ie.addEventListener("dispose",de),b.__depthDisposeCallback=de}b.__boundDepthTexture=ie}if(F.depthTexture&&!b.__autoAllocateDepthBuffer)if($)for(let ie=0;ie<6;ie++)ft(b.__webglFramebuffer[ie],F,ie);else{const ie=F.texture.mipmaps;ie&&ie.length>0?ft(b.__webglFramebuffer[0],F,0):ft(b.__webglFramebuffer,F,0)}else if($){b.__webglDepthbuffer=[];for(let ie=0;ie<6;ie++)if(t.bindFramebuffer(s.FRAMEBUFFER,b.__webglFramebuffer[ie]),b.__webglDepthbuffer[ie]===void 0)b.__webglDepthbuffer[ie]=s.createRenderbuffer(),Wt(b.__webglDepthbuffer[ie],F,!1);else{const de=F.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,be=b.__webglDepthbuffer[ie];s.bindRenderbuffer(s.RENDERBUFFER,be),s.framebufferRenderbuffer(s.FRAMEBUFFER,de,s.RENDERBUFFER,be)}}else{const ie=F.texture.mipmaps;if(ie&&ie.length>0?t.bindFramebuffer(s.FRAMEBUFFER,b.__webglFramebuffer[0]):t.bindFramebuffer(s.FRAMEBUFFER,b.__webglFramebuffer),b.__webglDepthbuffer===void 0)b.__webglDepthbuffer=s.createRenderbuffer(),Wt(b.__webglDepthbuffer,F,!1);else{const de=F.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,be=b.__webglDepthbuffer;s.bindRenderbuffer(s.RENDERBUFFER,be),s.framebufferRenderbuffer(s.FRAMEBUFFER,de,s.RENDERBUFFER,be)}}t.bindFramebuffer(s.FRAMEBUFFER,null)}function Mt(F,b,$){const ie=r.get(F);b!==void 0&&et(ie.__webglFramebuffer,F,F.texture,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,0),$!==void 0&&Nt(F)}function _t(F){const b=F.texture,$=r.get(F),ie=r.get(b);F.addEventListener("dispose",E);const de=F.textures,be=F.isWebGLCubeRenderTarget===!0,Ne=de.length>1;if(Ne||(ie.__webglTexture===void 0&&(ie.__webglTexture=s.createTexture()),ie.__version=b.version,d.memory.textures++),be){$.__webglFramebuffer=[];for(let fe=0;fe<6;fe++)if(b.mipmaps&&b.mipmaps.length>0){$.__webglFramebuffer[fe]=[];for(let ge=0;ge<b.mipmaps.length;ge++)$.__webglFramebuffer[fe][ge]=s.createFramebuffer()}else $.__webglFramebuffer[fe]=s.createFramebuffer()}else{if(b.mipmaps&&b.mipmaps.length>0){$.__webglFramebuffer=[];for(let fe=0;fe<b.mipmaps.length;fe++)$.__webglFramebuffer[fe]=s.createFramebuffer()}else $.__webglFramebuffer=s.createFramebuffer();if(Ne)for(let fe=0,ge=de.length;fe<ge;fe++){const Pe=r.get(de[fe]);Pe.__webglTexture===void 0&&(Pe.__webglTexture=s.createTexture(),d.memory.textures++)}if(F.samples>0&&qt(F)===!1){$.__webglMultisampledFramebuffer=s.createFramebuffer(),$.__webglColorRenderbuffer=[],t.bindFramebuffer(s.FRAMEBUFFER,$.__webglMultisampledFramebuffer);for(let fe=0;fe<de.length;fe++){const ge=de[fe];$.__webglColorRenderbuffer[fe]=s.createRenderbuffer(),s.bindRenderbuffer(s.RENDERBUFFER,$.__webglColorRenderbuffer[fe]);const Pe=l.convert(ge.format,ge.colorSpace),qe=l.convert(ge.type),Le=N(ge.internalFormat,Pe,qe,ge.normalized,ge.colorSpace,F.isXRRenderTarget===!0),Ce=It(F);s.renderbufferStorageMultisample(s.RENDERBUFFER,Ce,Le,F.width,F.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+fe,s.RENDERBUFFER,$.__webglColorRenderbuffer[fe])}s.bindRenderbuffer(s.RENDERBUFFER,null),F.depthBuffer&&($.__webglDepthRenderbuffer=s.createRenderbuffer(),Wt($.__webglDepthRenderbuffer,F,!0)),t.bindFramebuffer(s.FRAMEBUFFER,null)}}if(be){t.bindTexture(s.TEXTURE_CUBE_MAP,ie.__webglTexture),Ve(s.TEXTURE_CUBE_MAP,b);for(let fe=0;fe<6;fe++)if(b.mipmaps&&b.mipmaps.length>0)for(let ge=0;ge<b.mipmaps.length;ge++)et($.__webglFramebuffer[fe][ge],F,b,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+fe,ge);else et($.__webglFramebuffer[fe],F,b,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+fe,0);y(b)&&P(s.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ne){for(let fe=0,ge=de.length;fe<ge;fe++){const Pe=de[fe],qe=r.get(Pe);let Le=s.TEXTURE_2D;(F.isWebGL3DRenderTarget||F.isWebGLArrayRenderTarget)&&(Le=F.isWebGL3DRenderTarget?s.TEXTURE_3D:s.TEXTURE_2D_ARRAY),t.bindTexture(Le,qe.__webglTexture),Ve(Le,Pe),et($.__webglFramebuffer,F,Pe,s.COLOR_ATTACHMENT0+fe,Le,0),y(Pe)&&P(Le)}t.unbindTexture()}else{let fe=s.TEXTURE_2D;if((F.isWebGL3DRenderTarget||F.isWebGLArrayRenderTarget)&&(fe=F.isWebGL3DRenderTarget?s.TEXTURE_3D:s.TEXTURE_2D_ARRAY),t.bindTexture(fe,ie.__webglTexture),Ve(fe,b),b.mipmaps&&b.mipmaps.length>0)for(let ge=0;ge<b.mipmaps.length;ge++)et($.__webglFramebuffer[ge],F,b,s.COLOR_ATTACHMENT0,fe,ge);else et($.__webglFramebuffer,F,b,s.COLOR_ATTACHMENT0,fe,0);y(b)&&P(fe),t.unbindTexture()}F.depthBuffer&&Nt(F)}function Xt(F){const b=F.textures;for(let $=0,ie=b.length;$<ie;$++){const de=b[$];if(y(de)){const be=U(F),Ne=r.get(de).__webglTexture;t.bindTexture(be,Ne),P(be),t.unbindTexture()}}}const tn=[],nn=[];function Kt(F){if(F.samples>0){if(qt(F)===!1){const b=F.textures,$=F.width,ie=F.height;let de=s.COLOR_BUFFER_BIT;const be=F.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,Ne=r.get(F),fe=b.length>1;if(fe)for(let Pe=0;Pe<b.length;Pe++)t.bindFramebuffer(s.FRAMEBUFFER,Ne.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Pe,s.RENDERBUFFER,null),t.bindFramebuffer(s.FRAMEBUFFER,Ne.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+Pe,s.TEXTURE_2D,null,0);t.bindFramebuffer(s.READ_FRAMEBUFFER,Ne.__webglMultisampledFramebuffer);const ge=F.texture.mipmaps;ge&&ge.length>0?t.bindFramebuffer(s.DRAW_FRAMEBUFFER,Ne.__webglFramebuffer[0]):t.bindFramebuffer(s.DRAW_FRAMEBUFFER,Ne.__webglFramebuffer);for(let Pe=0;Pe<b.length;Pe++){if(F.resolveDepthBuffer&&(F.depthBuffer&&(de|=s.DEPTH_BUFFER_BIT),F.stencilBuffer&&F.resolveStencilBuffer&&(de|=s.STENCIL_BUFFER_BIT)),fe){s.framebufferRenderbuffer(s.READ_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.RENDERBUFFER,Ne.__webglColorRenderbuffer[Pe]);const qe=r.get(b[Pe]).__webglTexture;s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,qe,0)}s.blitFramebuffer(0,0,$,ie,0,0,$,ie,de,s.NEAREST),p===!0&&(tn.length=0,nn.length=0,tn.push(s.COLOR_ATTACHMENT0+Pe),F.depthBuffer&&F.resolveDepthBuffer===!1&&(tn.push(be),nn.push(be),s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,nn)),s.invalidateFramebuffer(s.READ_FRAMEBUFFER,tn))}if(t.bindFramebuffer(s.READ_FRAMEBUFFER,null),t.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),fe)for(let Pe=0;Pe<b.length;Pe++){t.bindFramebuffer(s.FRAMEBUFFER,Ne.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Pe,s.RENDERBUFFER,Ne.__webglColorRenderbuffer[Pe]);const qe=r.get(b[Pe]).__webglTexture;t.bindFramebuffer(s.FRAMEBUFFER,Ne.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+Pe,s.TEXTURE_2D,qe,0)}t.bindFramebuffer(s.DRAW_FRAMEBUFFER,Ne.__webglMultisampledFramebuffer)}else if(F.depthBuffer&&F.resolveDepthBuffer===!1&&p){const b=F.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,[b])}}}function It(F){return Math.min(o.maxSamples,F.samples)}function qt(F){const b=r.get(F);return F.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&b.__useRenderToTexture!==!1}function W(F){const b=d.render.frame;_.get(F)!==b&&(_.set(F,b),F.update())}function _n(F,b){const $=F.colorSpace,ie=F.format,de=F.type;return F.isCompressedTexture===!0||F.isVideoTexture===!0||$!==Sc&&$!==jr&&(St.getTransfer($)===Ft?(ie!==Ci||de!==pi)&&rt("WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):wt("WebGLTextures: Unsupported texture color space:",$)),b}function Tt(F){return typeof HTMLImageElement<"u"&&F instanceof HTMLImageElement?(m.width=F.naturalWidth||F.width,m.height=F.naturalHeight||F.height):typeof VideoFrame<"u"&&F instanceof VideoFrame?(m.width=F.displayWidth,m.height=F.displayHeight):(m.width=F.width,m.height=F.height),m}this.allocateTextureUnit=ue,this.resetTextureUnits=ce,this.getTextureUnits=he,this.setTextureUnits=Z,this.setTexture2D=q,this.setTexture2DArray=se,this.setTexture3D=le,this.setTextureCube=k,this.rebindTextures=Mt,this.setupRenderTarget=_t,this.updateRenderTargetMipmap=Xt,this.updateMultisampleRenderTarget=Kt,this.setupDepthRenderbuffer=Nt,this.setupFrameBufferTexture=et,this.useMultisampledRTT=qt,this.isReversedDepthBuffer=function(){return t.buffers.depth.getReversed()}}function rT(s,e){function t(r,o=jr){let l;const d=St.getTransfer(o);if(r===pi)return s.UNSIGNED_BYTE;if(r===rh)return s.UNSIGNED_SHORT_4_4_4_4;if(r===sh)return s.UNSIGNED_SHORT_5_5_5_1;if(r===Ax)return s.UNSIGNED_INT_5_9_9_9_REV;if(r===Cx)return s.UNSIGNED_INT_10F_11F_11F_REV;if(r===wx)return s.BYTE;if(r===Tx)return s.SHORT;if(r===wo)return s.UNSIGNED_SHORT;if(r===ih)return s.INT;if(r===Hi)return s.UNSIGNED_INT;if(r===Oi)return s.FLOAT;if(r===ur)return s.HALF_FLOAT;if(r===Nx)return s.ALPHA;if(r===Rx)return s.RGB;if(r===Ci)return s.RGBA;if(r===dr)return s.DEPTH_COMPONENT;if(r===Ss)return s.DEPTH_STENCIL;if(r===Px)return s.RED;if(r===ah)return s.RED_INTEGER;if(r===bs)return s.RG;if(r===oh)return s.RG_INTEGER;if(r===lh)return s.RGBA_INTEGER;if(r===dc||r===fc||r===hc||r===pc)if(d===Ft)if(l=e.get("WEBGL_compressed_texture_s3tc_srgb"),l!==null){if(r===dc)return l.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(r===fc)return l.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(r===hc)return l.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(r===pc)return l.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(l=e.get("WEBGL_compressed_texture_s3tc"),l!==null){if(r===dc)return l.COMPRESSED_RGB_S3TC_DXT1_EXT;if(r===fc)return l.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(r===hc)return l.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(r===pc)return l.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(r===gf||r===xf||r===vf||r===_f)if(l=e.get("WEBGL_compressed_texture_pvrtc"),l!==null){if(r===gf)return l.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(r===xf)return l.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(r===vf)return l.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(r===_f)return l.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(r===yf||r===Sf||r===Mf||r===bf||r===Ef||r===_c||r===wf)if(l=e.get("WEBGL_compressed_texture_etc"),l!==null){if(r===yf||r===Sf)return d===Ft?l.COMPRESSED_SRGB8_ETC2:l.COMPRESSED_RGB8_ETC2;if(r===Mf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:l.COMPRESSED_RGBA8_ETC2_EAC;if(r===bf)return l.COMPRESSED_R11_EAC;if(r===Ef)return l.COMPRESSED_SIGNED_R11_EAC;if(r===_c)return l.COMPRESSED_RG11_EAC;if(r===wf)return l.COMPRESSED_SIGNED_RG11_EAC}else return null;if(r===Tf||r===Af||r===Cf||r===Nf||r===Rf||r===Pf||r===Lf||r===If||r===Df||r===Uf||r===Ff||r===kf||r===Of||r===zf)if(l=e.get("WEBGL_compressed_texture_astc"),l!==null){if(r===Tf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:l.COMPRESSED_RGBA_ASTC_4x4_KHR;if(r===Af)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:l.COMPRESSED_RGBA_ASTC_5x4_KHR;if(r===Cf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:l.COMPRESSED_RGBA_ASTC_5x5_KHR;if(r===Nf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:l.COMPRESSED_RGBA_ASTC_6x5_KHR;if(r===Rf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:l.COMPRESSED_RGBA_ASTC_6x6_KHR;if(r===Pf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:l.COMPRESSED_RGBA_ASTC_8x5_KHR;if(r===Lf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:l.COMPRESSED_RGBA_ASTC_8x6_KHR;if(r===If)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:l.COMPRESSED_RGBA_ASTC_8x8_KHR;if(r===Df)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:l.COMPRESSED_RGBA_ASTC_10x5_KHR;if(r===Uf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:l.COMPRESSED_RGBA_ASTC_10x6_KHR;if(r===Ff)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:l.COMPRESSED_RGBA_ASTC_10x8_KHR;if(r===kf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:l.COMPRESSED_RGBA_ASTC_10x10_KHR;if(r===Of)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:l.COMPRESSED_RGBA_ASTC_12x10_KHR;if(r===zf)return d===Ft?l.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:l.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(r===Bf||r===Vf||r===Hf)if(l=e.get("EXT_texture_compression_bptc"),l!==null){if(r===Bf)return d===Ft?l.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:l.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(r===Vf)return l.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(r===Hf)return l.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(r===jf||r===Gf||r===yc||r===Wf)if(l=e.get("EXT_texture_compression_rgtc"),l!==null){if(r===jf)return l.COMPRESSED_RED_RGTC1_EXT;if(r===Gf)return l.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(r===yc)return l.COMPRESSED_RED_GREEN_RGTC2_EXT;if(r===Wf)return l.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return r===To?s.UNSIGNED_INT_24_8:s[r]!==void 0?s[r]:null}return{convert:t}}const sT=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,aT=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class oT{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t){if(this.texture===null){const r=new Hx(e.texture);(e.depthNear!==t.depthNear||e.depthFar!==t.depthFar)&&(this.depthNear=e.depthNear,this.depthFar=e.depthFar),this.texture=r}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,r=new ji({vertexShader:sT,fragmentShader:aT,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new mi(new Ic(20,20),r)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class lT extends ws{constructor(e,t){super();const r=this;let o=null,l=1,d=null,f="local-floor",p=1,m=null,_=null,S=null,x=null,M=null,w=null;const A=typeof XRWebGLBinding<"u",v=new oT,y={},P=t.getContextAttributes();let U=null,N=null;const L=[],R=[],D=new yt;let E=null;const I=new hi;I.viewport=new sn;const z=new hi;z.viewport=new sn;const B=[I,z],H=new x1;let ce=null,he=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(re){let _e=L[re];return _e===void 0&&(_e=new Pd,L[re]=_e),_e.getTargetRaySpace()},this.getControllerGrip=function(re){let _e=L[re];return _e===void 0&&(_e=new Pd,L[re]=_e),_e.getGripSpace()},this.getHand=function(re){let _e=L[re];return _e===void 0&&(_e=new Pd,L[re]=_e),_e.getHandSpace()};function Z(re){const _e=R.indexOf(re.inputSource);if(_e===-1)return;const me=L[_e];me!==void 0&&(me.update(re.inputSource,re.frame,m||d),me.dispatchEvent({type:re.type,data:re.inputSource}))}function ue(){o.removeEventListener("select",Z),o.removeEventListener("selectstart",Z),o.removeEventListener("selectend",Z),o.removeEventListener("squeeze",Z),o.removeEventListener("squeezestart",Z),o.removeEventListener("squeezeend",Z),o.removeEventListener("end",ue),o.removeEventListener("inputsourceschange",K);for(let re=0;re<L.length;re++){const _e=R[re];_e!==null&&(R[re]=null,L[re].disconnect(_e))}ce=null,he=null,v.reset();for(const re in y)delete y[re];e.setRenderTarget(U),M=null,x=null,S=null,o=null,N=null,Ve.stop(),r.isPresenting=!1,e.setPixelRatio(E),e.setSize(D.width,D.height,!1),r.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(re){l=re,r.isPresenting===!0&&rt("WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(re){f=re,r.isPresenting===!0&&rt("WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return m||d},this.setReferenceSpace=function(re){m=re},this.getBaseLayer=function(){return x!==null?x:M},this.getBinding=function(){return S===null&&A&&(S=new XRWebGLBinding(o,t)),S},this.getFrame=function(){return w},this.getSession=function(){return o},this.setSession=async function(re){if(o=re,o!==null){if(U=e.getRenderTarget(),o.addEventListener("select",Z),o.addEventListener("selectstart",Z),o.addEventListener("selectend",Z),o.addEventListener("squeeze",Z),o.addEventListener("squeezestart",Z),o.addEventListener("squeezeend",Z),o.addEventListener("end",ue),o.addEventListener("inputsourceschange",K),P.xrCompatible!==!0&&await t.makeXRCompatible(),E=e.getPixelRatio(),e.getSize(D),A&&"createProjectionLayer"in XRWebGLBinding.prototype){let me=null,Fe=null,Je=null;P.depth&&(Je=P.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,me=P.stencil?Ss:dr,Fe=P.stencil?To:Hi);const et={colorFormat:t.RGBA8,depthFormat:Je,scaleFactor:l};S=this.getBinding(),x=S.createProjectionLayer(et),o.updateRenderState({layers:[x]}),e.setPixelRatio(1),e.setSize(x.textureWidth,x.textureHeight,!1),N=new Vi(x.textureWidth,x.textureHeight,{format:Ci,type:pi,depthTexture:new va(x.textureWidth,x.textureHeight,Fe,void 0,void 0,void 0,void 0,void 0,void 0,me),stencilBuffer:P.stencil,colorSpace:e.outputColorSpace,samples:P.antialias?4:0,resolveDepthBuffer:x.ignoreDepthValues===!1,resolveStencilBuffer:x.ignoreDepthValues===!1})}else{const me={antialias:P.antialias,alpha:!0,depth:P.depth,stencil:P.stencil,framebufferScaleFactor:l};M=new XRWebGLLayer(o,t,me),o.updateRenderState({baseLayer:M}),e.setPixelRatio(1),e.setSize(M.framebufferWidth,M.framebufferHeight,!1),N=new Vi(M.framebufferWidth,M.framebufferHeight,{format:Ci,type:pi,colorSpace:e.outputColorSpace,stencilBuffer:P.stencil,resolveDepthBuffer:M.ignoreDepthValues===!1,resolveStencilBuffer:M.ignoreDepthValues===!1})}N.isXRRenderTarget=!0,this.setFoveation(p),m=null,d=await o.requestReferenceSpace(f),Ve.setContext(o),Ve.start(),r.isPresenting=!0,r.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(o!==null)return o.environmentBlendMode},this.getDepthTexture=function(){return v.getDepthTexture()};function K(re){for(let _e=0;_e<re.removed.length;_e++){const me=re.removed[_e],Fe=R.indexOf(me);Fe>=0&&(R[Fe]=null,L[Fe].disconnect(me))}for(let _e=0;_e<re.added.length;_e++){const me=re.added[_e];let Fe=R.indexOf(me);if(Fe===-1){for(let et=0;et<L.length;et++)if(et>=R.length){R.push(me),Fe=et;break}else if(R[et]===null){R[et]=me,Fe=et;break}if(Fe===-1)break}const Je=L[Fe];Je&&Je.connect(me)}}const q=new Y,se=new Y;function le(re,_e,me){q.setFromMatrixPosition(_e.matrixWorld),se.setFromMatrixPosition(me.matrixWorld);const Fe=q.distanceTo(se),Je=_e.projectionMatrix.elements,et=me.projectionMatrix.elements,Wt=Je[14]/(Je[10]-1),ft=Je[14]/(Je[10]+1),Nt=(Je[9]+1)/Je[5],Mt=(Je[9]-1)/Je[5],_t=(Je[8]-1)/Je[0],Xt=(et[8]+1)/et[0],tn=Wt*_t,nn=Wt*Xt,Kt=Fe/(-_t+Xt),It=Kt*-_t;if(_e.matrixWorld.decompose(re.position,re.quaternion,re.scale),re.translateX(It),re.translateZ(Kt),re.matrixWorld.compose(re.position,re.quaternion,re.scale),re.matrixWorldInverse.copy(re.matrixWorld).invert(),Je[10]===-1)re.projectionMatrix.copy(_e.projectionMatrix),re.projectionMatrixInverse.copy(_e.projectionMatrixInverse);else{const qt=Wt+Kt,W=ft+Kt,_n=tn-It,Tt=nn+(Fe-It),F=Nt*ft/W*qt,b=Mt*ft/W*qt;re.projectionMatrix.makePerspective(_n,Tt,F,b,qt,W),re.projectionMatrixInverse.copy(re.projectionMatrix).invert()}}function k(re,_e){_e===null?re.matrixWorld.copy(re.matrix):re.matrixWorld.multiplyMatrices(_e.matrixWorld,re.matrix),re.matrixWorldInverse.copy(re.matrixWorld).invert()}this.updateCamera=function(re){if(o===null)return;let _e=re.near,me=re.far;v.texture!==null&&(v.depthNear>0&&(_e=v.depthNear),v.depthFar>0&&(me=v.depthFar)),H.near=z.near=I.near=_e,H.far=z.far=I.far=me,(ce!==H.near||he!==H.far)&&(o.updateRenderState({depthNear:H.near,depthFar:H.far}),ce=H.near,he=H.far),H.layers.mask=re.layers.mask|6,I.layers.mask=H.layers.mask&-5,z.layers.mask=H.layers.mask&-3;const Fe=re.parent,Je=H.cameras;k(H,Fe);for(let et=0;et<Je.length;et++)k(Je[et],Fe);Je.length===2?le(H,I,z):H.projectionMatrix.copy(I.projectionMatrix),Q(re,H,Fe)};function Q(re,_e,me){me===null?re.matrix.copy(_e.matrixWorld):(re.matrix.copy(me.matrixWorld),re.matrix.invert(),re.matrix.multiply(_e.matrixWorld)),re.matrix.decompose(re.position,re.quaternion,re.scale),re.updateMatrixWorld(!0),re.projectionMatrix.copy(_e.projectionMatrix),re.projectionMatrixInverse.copy(_e.projectionMatrixInverse),re.isPerspectiveCamera&&(re.fov=Xf*2*Math.atan(1/re.projectionMatrix.elements[5]),re.zoom=1)}this.getCamera=function(){return H},this.getFoveation=function(){if(!(x===null&&M===null))return p},this.setFoveation=function(re){p=re,x!==null&&(x.fixedFoveation=re),M!==null&&M.fixedFoveation!==void 0&&(M.fixedFoveation=re)},this.hasDepthSensing=function(){return v.texture!==null},this.getDepthSensingMesh=function(){return v.getMesh(H)},this.getCameraTexture=function(re){return y[re]};let Ue=null;function $e(re,_e){if(_=_e.getViewerPose(m||d),w=_e,_!==null){const me=_.views;M!==null&&(e.setRenderTargetFramebuffer(N,M.framebuffer),e.setRenderTarget(N));let Fe=!1;me.length!==H.cameras.length&&(H.cameras.length=0,Fe=!0);for(let ft=0;ft<me.length;ft++){const Nt=me[ft];let Mt=null;if(M!==null)Mt=M.getViewport(Nt);else{const Xt=S.getViewSubImage(x,Nt);Mt=Xt.viewport,ft===0&&(e.setRenderTargetTextures(N,Xt.colorTexture,Xt.depthStencilTexture),e.setRenderTarget(N))}let _t=B[ft];_t===void 0&&(_t=new hi,_t.layers.enable(ft),_t.viewport=new sn,B[ft]=_t),_t.matrix.fromArray(Nt.transform.matrix),_t.matrix.decompose(_t.position,_t.quaternion,_t.scale),_t.projectionMatrix.fromArray(Nt.projectionMatrix),_t.projectionMatrixInverse.copy(_t.projectionMatrix).invert(),_t.viewport.set(Mt.x,Mt.y,Mt.width,Mt.height),ft===0&&(H.matrix.copy(_t.matrix),H.matrix.decompose(H.position,H.quaternion,H.scale)),Fe===!0&&H.cameras.push(_t)}const Je=o.enabledFeatures;if(Je&&Je.includes("depth-sensing")&&o.depthUsage=="gpu-optimized"&&A){S=r.getBinding();const ft=S.getDepthInformation(me[0]);ft&&ft.isValid&&ft.texture&&v.init(ft,o.renderState)}if(Je&&Je.includes("camera-access")&&A){e.state.unbindTexture(),S=r.getBinding();for(let ft=0;ft<me.length;ft++){const Nt=me[ft].camera;if(Nt){let Mt=y[Nt];Mt||(Mt=new Hx,y[Nt]=Mt);const _t=S.getCameraImage(Nt);Mt.sourceTexture=_t}}}}for(let me=0;me<L.length;me++){const Fe=R[me],Je=L[me];Fe!==null&&Je!==void 0&&Je.update(Fe,_e,m||d)}Ue&&Ue(re,_e),_e.detectedPlanes&&r.dispatchEvent({type:"planesdetected",data:_e}),w=null}const Ve=new Xx;Ve.setAnimationLoop($e),this.setAnimationLoop=function(re){Ue=re},this.dispose=function(){}}}const cT=new en,Jx=new ut;Jx.set(-1,0,0,0,1,0,0,0,1);function uT(s,e){function t(v,y){v.matrixAutoUpdate===!0&&v.updateMatrix(),y.value.copy(v.matrix)}function r(v,y){y.color.getRGB(v.fogColor.value,jx(s)),y.isFog?(v.fogNear.value=y.near,v.fogFar.value=y.far):y.isFogExp2&&(v.fogDensity.value=y.density)}function o(v,y,P,U,N){y.isNodeMaterial?y.uniformsNeedUpdate=!1:y.isMeshBasicMaterial?l(v,y):y.isMeshLambertMaterial?(l(v,y),y.envMap&&(v.envMapIntensity.value=y.envMapIntensity)):y.isMeshToonMaterial?(l(v,y),S(v,y)):y.isMeshPhongMaterial?(l(v,y),_(v,y),y.envMap&&(v.envMapIntensity.value=y.envMapIntensity)):y.isMeshStandardMaterial?(l(v,y),x(v,y),y.isMeshPhysicalMaterial&&M(v,y,N)):y.isMeshMatcapMaterial?(l(v,y),w(v,y)):y.isMeshDepthMaterial?l(v,y):y.isMeshDistanceMaterial?(l(v,y),A(v,y)):y.isMeshNormalMaterial?l(v,y):y.isLineBasicMaterial?(d(v,y),y.isLineDashedMaterial&&f(v,y)):y.isPointsMaterial?p(v,y,P,U):y.isSpriteMaterial?m(v,y):y.isShadowMaterial?(v.color.value.copy(y.color),v.opacity.value=y.opacity):y.isShaderMaterial&&(y.uniformsNeedUpdate=!1)}function l(v,y){v.opacity.value=y.opacity,y.color&&v.diffuse.value.copy(y.color),y.emissive&&v.emissive.value.copy(y.emissive).multiplyScalar(y.emissiveIntensity),y.map&&(v.map.value=y.map,t(y.map,v.mapTransform)),y.alphaMap&&(v.alphaMap.value=y.alphaMap,t(y.alphaMap,v.alphaMapTransform)),y.bumpMap&&(v.bumpMap.value=y.bumpMap,t(y.bumpMap,v.bumpMapTransform),v.bumpScale.value=y.bumpScale,y.side===Zn&&(v.bumpScale.value*=-1)),y.normalMap&&(v.normalMap.value=y.normalMap,t(y.normalMap,v.normalMapTransform),v.normalScale.value.copy(y.normalScale),y.side===Zn&&v.normalScale.value.negate()),y.displacementMap&&(v.displacementMap.value=y.displacementMap,t(y.displacementMap,v.displacementMapTransform),v.displacementScale.value=y.displacementScale,v.displacementBias.value=y.displacementBias),y.emissiveMap&&(v.emissiveMap.value=y.emissiveMap,t(y.emissiveMap,v.emissiveMapTransform)),y.specularMap&&(v.specularMap.value=y.specularMap,t(y.specularMap,v.specularMapTransform)),y.alphaTest>0&&(v.alphaTest.value=y.alphaTest);const P=e.get(y),U=P.envMap,N=P.envMapRotation;U&&(v.envMap.value=U,v.envMapRotation.value.setFromMatrix4(cT.makeRotationFromEuler(N)).transpose(),U.isCubeTexture&&U.isRenderTargetTexture===!1&&v.envMapRotation.value.premultiply(Jx),v.reflectivity.value=y.reflectivity,v.ior.value=y.ior,v.refractionRatio.value=y.refractionRatio),y.lightMap&&(v.lightMap.value=y.lightMap,v.lightMapIntensity.value=y.lightMapIntensity,t(y.lightMap,v.lightMapTransform)),y.aoMap&&(v.aoMap.value=y.aoMap,v.aoMapIntensity.value=y.aoMapIntensity,t(y.aoMap,v.aoMapTransform))}function d(v,y){v.diffuse.value.copy(y.color),v.opacity.value=y.opacity,y.map&&(v.map.value=y.map,t(y.map,v.mapTransform))}function f(v,y){v.dashSize.value=y.dashSize,v.totalSize.value=y.dashSize+y.gapSize,v.scale.value=y.scale}function p(v,y,P,U){v.diffuse.value.copy(y.color),v.opacity.value=y.opacity,v.size.value=y.size*P,v.scale.value=U*.5,y.map&&(v.map.value=y.map,t(y.map,v.uvTransform)),y.alphaMap&&(v.alphaMap.value=y.alphaMap,t(y.alphaMap,v.alphaMapTransform)),y.alphaTest>0&&(v.alphaTest.value=y.alphaTest)}function m(v,y){v.diffuse.value.copy(y.color),v.opacity.value=y.opacity,v.rotation.value=y.rotation,y.map&&(v.map.value=y.map,t(y.map,v.mapTransform)),y.alphaMap&&(v.alphaMap.value=y.alphaMap,t(y.alphaMap,v.alphaMapTransform)),y.alphaTest>0&&(v.alphaTest.value=y.alphaTest)}function _(v,y){v.specular.value.copy(y.specular),v.shininess.value=Math.max(y.shininess,1e-4)}function S(v,y){y.gradientMap&&(v.gradientMap.value=y.gradientMap)}function x(v,y){v.metalness.value=y.metalness,y.metalnessMap&&(v.metalnessMap.value=y.metalnessMap,t(y.metalnessMap,v.metalnessMapTransform)),v.roughness.value=y.roughness,y.roughnessMap&&(v.roughnessMap.value=y.roughnessMap,t(y.roughnessMap,v.roughnessMapTransform)),y.envMap&&(v.envMapIntensity.value=y.envMapIntensity)}function M(v,y,P){v.ior.value=y.ior,y.sheen>0&&(v.sheenColor.value.copy(y.sheenColor).multiplyScalar(y.sheen),v.sheenRoughness.value=y.sheenRoughness,y.sheenColorMap&&(v.sheenColorMap.value=y.sheenColorMap,t(y.sheenColorMap,v.sheenColorMapTransform)),y.sheenRoughnessMap&&(v.sheenRoughnessMap.value=y.sheenRoughnessMap,t(y.sheenRoughnessMap,v.sheenRoughnessMapTransform))),y.clearcoat>0&&(v.clearcoat.value=y.clearcoat,v.clearcoatRoughness.value=y.clearcoatRoughness,y.clearcoatMap&&(v.clearcoatMap.value=y.clearcoatMap,t(y.clearcoatMap,v.clearcoatMapTransform)),y.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=y.clearcoatRoughnessMap,t(y.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),y.clearcoatNormalMap&&(v.clearcoatNormalMap.value=y.clearcoatNormalMap,t(y.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(y.clearcoatNormalScale),y.side===Zn&&v.clearcoatNormalScale.value.negate())),y.dispersion>0&&(v.dispersion.value=y.dispersion),y.iridescence>0&&(v.iridescence.value=y.iridescence,v.iridescenceIOR.value=y.iridescenceIOR,v.iridescenceThicknessMinimum.value=y.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=y.iridescenceThicknessRange[1],y.iridescenceMap&&(v.iridescenceMap.value=y.iridescenceMap,t(y.iridescenceMap,v.iridescenceMapTransform)),y.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=y.iridescenceThicknessMap,t(y.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),y.transmission>0&&(v.transmission.value=y.transmission,v.transmissionSamplerMap.value=P.texture,v.transmissionSamplerSize.value.set(P.width,P.height),y.transmissionMap&&(v.transmissionMap.value=y.transmissionMap,t(y.transmissionMap,v.transmissionMapTransform)),v.thickness.value=y.thickness,y.thicknessMap&&(v.thicknessMap.value=y.thicknessMap,t(y.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=y.attenuationDistance,v.attenuationColor.value.copy(y.attenuationColor)),y.anisotropy>0&&(v.anisotropyVector.value.set(y.anisotropy*Math.cos(y.anisotropyRotation),y.anisotropy*Math.sin(y.anisotropyRotation)),y.anisotropyMap&&(v.anisotropyMap.value=y.anisotropyMap,t(y.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=y.specularIntensity,v.specularColor.value.copy(y.specularColor),y.specularColorMap&&(v.specularColorMap.value=y.specularColorMap,t(y.specularColorMap,v.specularColorMapTransform)),y.specularIntensityMap&&(v.specularIntensityMap.value=y.specularIntensityMap,t(y.specularIntensityMap,v.specularIntensityMapTransform))}function w(v,y){y.matcap&&(v.matcap.value=y.matcap)}function A(v,y){const P=e.get(y).light;v.referencePosition.value.setFromMatrixPosition(P.matrixWorld),v.nearDistance.value=P.shadow.camera.near,v.farDistance.value=P.shadow.camera.far}return{refreshFogUniforms:r,refreshMaterialUniforms:o}}function dT(s,e,t,r){let o={},l={},d=[];const f=s.getParameter(s.MAX_UNIFORM_BUFFER_BINDINGS);function p(N,L){const R=L.program;r.uniformBlockBinding(N,R)}function m(N,L){let R=o[N.id];R===void 0&&(v(N),R=_(N),o[N.id]=R,N.addEventListener("dispose",P));const D=L.program;r.updateUBOMapping(N,D);const E=e.render.frame;l[N.id]!==E&&(x(N),l[N.id]=E)}function _(N){const L=S();N.__bindingPointIndex=L;const R=s.createBuffer(),D=N.__size,E=N.usage;return s.bindBuffer(s.UNIFORM_BUFFER,R),s.bufferData(s.UNIFORM_BUFFER,D,E),s.bindBuffer(s.UNIFORM_BUFFER,null),s.bindBufferBase(s.UNIFORM_BUFFER,L,R),R}function S(){for(let N=0;N<f;N++)if(d.indexOf(N)===-1)return d.push(N),N;return wt("WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function x(N){const L=o[N.id],R=N.uniforms,D=N.__cache;s.bindBuffer(s.UNIFORM_BUFFER,L);for(let E=0,I=R.length;E<I;E++){const z=R[E];if(Array.isArray(z))for(let B=0,H=z.length;B<H;B++)M(z[B],E,B,D);else M(z,E,0,D)}s.bindBuffer(s.UNIFORM_BUFFER,null)}function M(N,L,R,D){if(A(N,L,R,D)===!0){const E=N.__offset,I=N.value;if(Array.isArray(I)){let z=0;for(let B=0;B<I.length;B++){const H=I[B],ce=y(H);w(H,N.__data,z),typeof H!="number"&&typeof H!="boolean"&&!H.isMatrix3&&!ArrayBuffer.isView(H)&&(z+=ce.storage/Float32Array.BYTES_PER_ELEMENT)}}else w(I,N.__data,0);s.bufferSubData(s.UNIFORM_BUFFER,E,N.__data)}}function w(N,L,R){typeof N=="number"||typeof N=="boolean"?L[0]=N:N.isMatrix3?(L[0]=N.elements[0],L[1]=N.elements[1],L[2]=N.elements[2],L[3]=0,L[4]=N.elements[3],L[5]=N.elements[4],L[6]=N.elements[5],L[7]=0,L[8]=N.elements[6],L[9]=N.elements[7],L[10]=N.elements[8],L[11]=0):ArrayBuffer.isView(N)?L.set(new N.constructor(N.buffer,N.byteOffset,L.length)):N.toArray(L,R)}function A(N,L,R,D){const E=N.value,I=L+"_"+R;if(D[I]===void 0)return typeof E=="number"||typeof E=="boolean"?D[I]=E:ArrayBuffer.isView(E)?D[I]=E.slice():D[I]=E.clone(),!0;{const z=D[I];if(typeof E=="number"||typeof E=="boolean"){if(z!==E)return D[I]=E,!0}else{if(ArrayBuffer.isView(E))return!0;if(z.equals(E)===!1)return z.copy(E),!0}}return!1}function v(N){const L=N.uniforms;let R=0;const D=16;for(let I=0,z=L.length;I<z;I++){const B=Array.isArray(L[I])?L[I]:[L[I]];for(let H=0,ce=B.length;H<ce;H++){const he=B[H],Z=Array.isArray(he.value)?he.value:[he.value];for(let ue=0,K=Z.length;ue<K;ue++){const q=Z[ue],se=y(q),le=R%D,k=le%se.boundary,Q=le+k;R+=k,Q!==0&&D-Q<se.storage&&(R+=D-Q),he.__data=new Float32Array(se.storage/Float32Array.BYTES_PER_ELEMENT),he.__offset=R,R+=se.storage}}}const E=R%D;return E>0&&(R+=D-E),N.__size=R,N.__cache={},this}function y(N){const L={boundary:0,storage:0};return typeof N=="number"||typeof N=="boolean"?(L.boundary=4,L.storage=4):N.isVector2?(L.boundary=8,L.storage=8):N.isVector3||N.isColor?(L.boundary=16,L.storage=12):N.isVector4?(L.boundary=16,L.storage=16):N.isMatrix3?(L.boundary=48,L.storage=48):N.isMatrix4?(L.boundary=64,L.storage=64):N.isTexture?rt("WebGLRenderer: Texture samplers can not be part of an uniforms group."):ArrayBuffer.isView(N)?(L.boundary=16,L.storage=N.byteLength):rt("WebGLRenderer: Unsupported uniform value type.",N),L}function P(N){const L=N.target;L.removeEventListener("dispose",P);const R=d.indexOf(L.__bindingPointIndex);d.splice(R,1),s.deleteBuffer(o[L.id]),delete o[L.id],delete l[L.id]}function U(){for(const N in o)s.deleteBuffer(o[N]);d=[],o={},l={}}return{bind:p,update:m,dispose:U}}const fT=new Uint16Array([12469,15057,12620,14925,13266,14620,13807,14376,14323,13990,14545,13625,14713,13328,14840,12882,14931,12528,14996,12233,15039,11829,15066,11525,15080,11295,15085,10976,15082,10705,15073,10495,13880,14564,13898,14542,13977,14430,14158,14124,14393,13732,14556,13410,14702,12996,14814,12596,14891,12291,14937,11834,14957,11489,14958,11194,14943,10803,14921,10506,14893,10278,14858,9960,14484,14039,14487,14025,14499,13941,14524,13740,14574,13468,14654,13106,14743,12678,14818,12344,14867,11893,14889,11509,14893,11180,14881,10751,14852,10428,14812,10128,14765,9754,14712,9466,14764,13480,14764,13475,14766,13440,14766,13347,14769,13070,14786,12713,14816,12387,14844,11957,14860,11549,14868,11215,14855,10751,14825,10403,14782,10044,14729,9651,14666,9352,14599,9029,14967,12835,14966,12831,14963,12804,14954,12723,14936,12564,14917,12347,14900,11958,14886,11569,14878,11247,14859,10765,14828,10401,14784,10011,14727,9600,14660,9289,14586,8893,14508,8533,15111,12234,15110,12234,15104,12216,15092,12156,15067,12010,15028,11776,14981,11500,14942,11205,14902,10752,14861,10393,14812,9991,14752,9570,14682,9252,14603,8808,14519,8445,14431,8145,15209,11449,15208,11451,15202,11451,15190,11438,15163,11384,15117,11274,15055,10979,14994,10648,14932,10343,14871,9936,14803,9532,14729,9218,14645,8742,14556,8381,14461,8020,14365,7603,15273,10603,15272,10607,15267,10619,15256,10631,15231,10614,15182,10535,15118,10389,15042,10167,14963,9787,14883,9447,14800,9115,14710,8665,14615,8318,14514,7911,14411,7507,14279,7198,15314,9675,15313,9683,15309,9712,15298,9759,15277,9797,15229,9773,15166,9668,15084,9487,14995,9274,14898,8910,14800,8539,14697,8234,14590,7790,14479,7409,14367,7067,14178,6621,15337,8619,15337,8631,15333,8677,15325,8769,15305,8871,15264,8940,15202,8909,15119,8775,15022,8565,14916,8328,14804,8009,14688,7614,14569,7287,14448,6888,14321,6483,14088,6171,15350,7402,15350,7419,15347,7480,15340,7613,15322,7804,15287,7973,15229,8057,15148,8012,15046,7846,14933,7611,14810,7357,14682,7069,14552,6656,14421,6316,14251,5948,14007,5528,15356,5942,15356,5977,15353,6119,15348,6294,15332,6551,15302,6824,15249,7044,15171,7122,15070,7050,14949,6861,14818,6611,14679,6349,14538,6067,14398,5651,14189,5311,13935,4958,15359,4123,15359,4153,15356,4296,15353,4646,15338,5160,15311,5508,15263,5829,15188,6042,15088,6094,14966,6001,14826,5796,14678,5543,14527,5287,14377,4985,14133,4586,13869,4257,15360,1563,15360,1642,15358,2076,15354,2636,15341,3350,15317,4019,15273,4429,15203,4732,15105,4911,14981,4932,14836,4818,14679,4621,14517,4386,14359,4156,14083,3795,13808,3437,15360,122,15360,137,15358,285,15355,636,15344,1274,15322,2177,15281,2765,15215,3223,15120,3451,14995,3569,14846,3567,14681,3466,14511,3305,14344,3121,14037,2800,13753,2467,15360,0,15360,1,15359,21,15355,89,15346,253,15325,479,15287,796,15225,1148,15133,1492,15008,1749,14856,1882,14685,1886,14506,1783,14324,1608,13996,1398,13702,1183]);let Fi=null;function hT(){return Fi===null&&(Fi=new JS(fT,16,16,bs,ur),Fi.name="DFG_LUT",Fi.minFilter=In,Fi.magFilter=In,Fi.wrapS=ar,Fi.wrapT=ar,Fi.generateMipmaps=!1,Fi.needsUpdate=!0),Fi}class pT{constructor(e={}){const{canvas:t=RS(),context:r=null,depth:o=!0,stencil:l=!1,alpha:d=!1,antialias:f=!1,premultipliedAlpha:p=!0,preserveDrawingBuffer:m=!1,powerPreference:_="default",failIfMajorPerformanceCaveat:S=!1,reversedDepthBuffer:x=!1,outputBufferType:M=pi}=e;this.isWebGLRenderer=!0;let w;if(r!==null){if(typeof WebGLRenderingContext<"u"&&r instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");w=r.getContextAttributes().alpha}else w=d;const A=M,v=new Set([lh,oh,ah]),y=new Set([pi,Hi,wo,To,rh,sh]),P=new Uint32Array(4),U=new Int32Array(4),N=new Y;let L=null,R=null;const D=[],E=[];let I=null;this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=Bi,this.toneMappingExposure=1,this.transmissionResolutionScale=1;const z=this;let B=!1,H=null,ce=null,he=null,Z=null;this._outputColorSpace=fi;let ue=0,K=0,q=null,se=-1,le=null;const k=new sn,Q=new sn;let Ue=null;const $e=new Ct(0);let Ve=0,re=t.width,_e=t.height,me=1,Fe=null,Je=null;const et=new sn(0,0,re,_e),Wt=new sn(0,0,re,_e);let ft=!1;const Nt=new Ox;let Mt=!1,_t=!1;const Xt=new en,tn=new Y,nn=new sn,Kt={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let It=!1;function qt(){return q===null?me:1}let W=r;function _n(C,X){return t.getContext(C,X)}try{const C={alpha:!0,depth:o,stencil:l,antialias:f,premultipliedAlpha:p,preserveDrawingBuffer:m,powerPreference:_,failIfMajorPerformanceCaveat:S};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${nh}`),t.addEventListener("webglcontextlost",kt,!1),t.addEventListener("webglcontextrestored",Rt,!1),t.addEventListener("webglcontextcreationerror",Tn,!1),W===null){const X="webgl2";if(W=_n(X,C),W===null)throw _n(X)?new Error("THREE.WebGLRenderer: Error creating WebGL context with your selected attributes."):new Error("THREE.WebGLRenderer: Error creating WebGL context.")}}catch(C){throw wt("WebGLRenderer: "+C.message),C}let Tt,F,b,$,ie,de,be,Ne,fe,ge,Pe,qe,Le,Ce,Qe,tt,at,j,Ae,pe,Re,Ie,ve;function Ge(){Tt=new hE(W),Tt.init(),Re=new rT(W,Tt),F=new sE(W,Tt,e,Re),b=new nT(W,Tt),F.reversedDepthBuffer&&x&&b.buffers.depth.setReversed(!0),ce=W.createFramebuffer(),he=W.createFramebuffer(),Z=W.createFramebuffer(),$=new gE(W),ie=new Hw,de=new iT(W,Tt,b,ie,F,Re,$),be=new fE(z),Ne=new y1(W),Ie=new iE(W,Ne),fe=new pE(W,Ne,$,Ie),ge=new vE(W,fe,Ne,Ie,$),j=new xE(W,F,de),Qe=new aE(ie),Pe=new Vw(z,be,Tt,F,Ie,Qe),qe=new uT(z,ie),Le=new Gw,Ce=new Kw(Tt),at=new nE(z,be,b,ge,w,p),tt=new tT(z,ge,F),ve=new dT(W,$,F,b),Ae=new rE(W,Tt,$),pe=new mE(W,Tt,$),$.programs=Pe.programs,z.capabilities=F,z.extensions=Tt,z.properties=ie,z.renderLists=Le,z.shadowMap=tt,z.state=b,z.info=$}Ge(),A!==pi&&(I=new yE(A,t.width,t.height,f,o,l));const He=new lT(z,W);this.xr=He,this.getContext=function(){return W},this.getContextAttributes=function(){return W.getContextAttributes()},this.forceContextLoss=function(){const C=Tt.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){const C=Tt.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return me},this.setPixelRatio=function(C){C!==void 0&&(me=C,this.setSize(re,_e,!1))},this.getSize=function(C){return C.set(re,_e)},this.setSize=function(C,X,ae=!0){if(He.isPresenting){rt("WebGLRenderer: Can't change size while VR device is presenting.");return}re=C,_e=X,t.width=Math.floor(C*me),t.height=Math.floor(X*me),ae===!0&&(t.style.width=C+"px",t.style.height=X+"px"),I!==null&&I.setSize(t.width,t.height),this.setViewport(0,0,C,X)},this.getDrawingBufferSize=function(C){return C.set(re*me,_e*me).floor()},this.setDrawingBufferSize=function(C,X,ae){re=C,_e=X,me=ae,t.width=Math.floor(C*ae),t.height=Math.floor(X*ae),this.setViewport(0,0,C,X)},this.setEffects=function(C){if(A===pi){wt("WebGLRenderer: setEffects() requires outputBufferType set to HalfFloatType or FloatType.");return}if(C){for(let X=0;X<C.length;X++)if(C[X].isOutputPass===!0){rt("WebGLRenderer: OutputPass is not needed in setEffects(). Tone mapping and color space conversion are applied automatically.");break}}I.setEffects(C||[])},this.getCurrentViewport=function(C){return C.copy(k)},this.getViewport=function(C){return C.copy(et)},this.setViewport=function(C,X,ae,te){C.isVector4?et.set(C.x,C.y,C.z,C.w):et.set(C,X,ae,te),b.viewport(k.copy(et).multiplyScalar(me).round())},this.getScissor=function(C){return C.copy(Wt)},this.setScissor=function(C,X,ae,te){C.isVector4?Wt.set(C.x,C.y,C.z,C.w):Wt.set(C,X,ae,te),b.scissor(Q.copy(Wt).multiplyScalar(me).round())},this.getScissorTest=function(){return ft},this.setScissorTest=function(C){b.setScissorTest(ft=C)},this.setOpaqueSort=function(C){Fe=C},this.setTransparentSort=function(C){Je=C},this.getClearColor=function(C){return C.copy(at.getClearColor())},this.setClearColor=function(){at.setClearColor(...arguments)},this.getClearAlpha=function(){return at.getClearAlpha()},this.setClearAlpha=function(){at.setClearAlpha(...arguments)},this.clear=function(C=!0,X=!0,ae=!0){let te=0;if(C){let ee=!1;if(q!==null){const Te=q.texture.format;ee=v.has(Te)}if(ee){const Te=q.texture.type,ze=y.has(Te),we=at.getClearColor(),We=at.getClearAlpha(),Ze=we.r,lt=we.g,ct=we.b;ze?(P[0]=Ze,P[1]=lt,P[2]=ct,P[3]=We,W.clearBufferuiv(W.COLOR,0,P)):(U[0]=Ze,U[1]=lt,U[2]=ct,U[3]=We,W.clearBufferiv(W.COLOR,0,U))}else te|=W.COLOR_BUFFER_BIT}X&&(te|=W.DEPTH_BUFFER_BIT,this.state.buffers.depth.setMask(!0)),ae&&(te|=W.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),te!==0&&W.clear(te)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.setNodesHandler=function(C){C.setRenderer(this),H=C},this.dispose=function(){t.removeEventListener("webglcontextlost",kt,!1),t.removeEventListener("webglcontextrestored",Rt,!1),t.removeEventListener("webglcontextcreationerror",Tn,!1),at.dispose(),Le.dispose(),Ce.dispose(),ie.dispose(),be.dispose(),ge.dispose(),Ie.dispose(),ve.dispose(),Pe.dispose(),He.dispose(),He.removeEventListener("sessionstart",Lo),He.removeEventListener("sessionend",Io),Un.stop()};function kt(C){C.preventDefault(),rg("WebGLRenderer: Context Lost."),B=!0}function Rt(){rg("WebGLRenderer: Context Restored."),B=!1;const C=$.autoReset,X=tt.enabled,ae=tt.autoUpdate,te=tt.needsUpdate,ee=tt.type;Ge(),$.autoReset=C,tt.enabled=X,tt.autoUpdate=ae,tt.needsUpdate=te,tt.type=ee}function Tn(C){wt("WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}function ri(C){const X=C.target;X.removeEventListener("dispose",ri),$r(X)}function $r(C){Ts(C),ie.remove(C)}function Ts(C){const X=ie.get(C).programs;X!==void 0&&(X.forEach(function(ae){Pe.releaseProgram(ae)}),C.isShaderMaterial&&Pe.releaseShaderCache(C))}this.renderBufferDirect=function(C,X,ae,te,ee,Te){X===null&&(X=Kt);const ze=ee.isMesh&&ee.matrixWorld.determinantAffine()<0,we=Zt(C,X,ae,te,ee);b.setMaterial(te,ze);let We=ae.index,Ze=1;if(te.wireframe===!0){if(We=fe.getWireframeAttribute(ae),We===void 0)return;Ze=2}const lt=ae.drawRange,ct=ae.attributes.position;let Ye=lt.start*Ze,bt=(lt.start+lt.count)*Ze;Te!==null&&(Ye=Math.max(Ye,Te.start*Ze),bt=Math.min(bt,(Te.start+Te.count)*Ze)),We!==null?(Ye=Math.max(Ye,0),bt=Math.min(bt,We.count)):ct!=null&&(Ye=Math.max(Ye,0),bt=Math.min(bt,ct.count));const Ot=bt-Ye;if(Ot<0||Ot===1/0)return;Ie.setup(ee,te,we,ae,We);let Yt,Dt=Ae;if(We!==null&&(Yt=Ne.get(We),Dt=pe,Dt.setIndex(Yt)),ee.isMesh)te.wireframe===!0?(b.setLineWidth(te.wireframeLinewidth*qt()),Dt.setMode(W.LINES)):Dt.setMode(W.TRIANGLES);else if(ee.isLine){let on=te.linewidth;on===void 0&&(on=1),b.setLineWidth(on*qt()),ee.isLineSegments?Dt.setMode(W.LINES):ee.isLineLoop?Dt.setMode(W.LINE_LOOP):Dt.setMode(W.LINE_STRIP)}else ee.isPoints?Dt.setMode(W.POINTS):ee.isSprite&&Dt.setMode(W.TRIANGLES);if(ee.isBatchedMesh)if(Tt.get("WEBGL_multi_draw"))Dt.renderMultiDraw(ee._multiDrawStarts,ee._multiDrawCounts,ee._multiDrawCount);else{const on=ee._multiDrawStarts,ke=ee._multiDrawCounts,yn=ee._multiDrawCount,mt=We?Ne.get(We).bytesPerElement:1,Hn=ie.get(te).currentProgram.getUniforms();for(let jn=0;jn<yn;jn++)Hn.setValue(W,"_gl_DrawID",jn),Dt.render(on[jn]/mt,ke[jn])}else if(ee.isInstancedMesh)Dt.renderInstances(Ye,Ot,ee.count);else if(ae.isInstancedBufferGeometry){const on=ae._maxInstanceCount!==void 0?ae._maxInstanceCount:1/0,ke=Math.min(ae.instanceCount,on);Dt.renderInstances(Ye,Ot,ke)}else Dt.render(Ye,Ot)};function Kr(C,X,ae){C.transparent===!0&&C.side===sr&&C.forceSinglePass===!1?(C.side=Zn,C.needsUpdate=!0,Jr(C,X,ae),C.side=Xr,C.needsUpdate=!0,Jr(C,X,ae),C.side=sr):Jr(C,X,ae)}this.compile=function(C,X,ae=null){ae===null&&(ae=C),R=Ce.get(ae),R.init(X),E.push(R),ae.traverseVisible(function(ee){ee.isLight&&ee.layers.test(X.layers)&&(R.pushLight(ee),ee.castShadow&&R.pushShadow(ee))}),C!==ae&&C.traverseVisible(function(ee){ee.isLight&&ee.layers.test(X.layers)&&(R.pushLight(ee),ee.castShadow&&R.pushShadow(ee))}),R.setupLights();const te=new Set;return C.traverse(function(ee){if(!(ee.isMesh||ee.isPoints||ee.isLine||ee.isSprite))return;const Te=ee.material;if(Te)if(Array.isArray(Te))for(let ze=0;ze<Te.length;ze++){const we=Te[ze];Kr(we,ae,ee),te.add(we)}else Kr(Te,ae,ee),te.add(Te)}),R=E.pop(),te},this.compileAsync=function(C,X,ae=null){const te=this.compile(C,X,ae);return new Promise(ee=>{function Te(){if(te.forEach(function(ze){ie.get(ze).currentProgram.isReady()&&te.delete(ze)}),te.size===0){ee(C);return}setTimeout(Te,10)}Tt.get("KHR_parallel_shader_compile")!==null?Te():setTimeout(Te,10)})};let Zr=null;function Fc(C){Zr&&Zr(C)}function Lo(){Un.stop()}function Io(){Un.start()}const Un=new Xx;Un.setAnimationLoop(Fc),typeof self<"u"&&Un.setContext(self),this.setAnimationLoop=function(C){Zr=C,He.setAnimationLoop(C),C===null?Un.stop():Un.start()},He.addEventListener("sessionstart",Lo),He.addEventListener("sessionend",Io),this.render=function(C,X){if(X!==void 0&&X.isCamera!==!0){wt("WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(B===!0)return;H!==null&&H.renderStart(C,X);const ae=He.enabled===!0&&He.isPresenting===!0,te=I!==null&&(q===null||ae)&&I.begin(z,q);if(C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),X.parent===null&&X.matrixWorldAutoUpdate===!0&&X.updateMatrixWorld(),He.enabled===!0&&He.isPresenting===!0&&(I===null||I.isCompositing()===!1)&&(He.cameraAutoUpdate===!0&&He.updateCamera(X),X=He.getCamera()),C.isScene===!0&&C.onBeforeRender(z,C,X,q),R=Ce.get(C,E.length),R.init(X),R.state.textureUnits=de.getTextureUnits(),E.push(R),Xt.multiplyMatrices(X.projectionMatrix,X.matrixWorldInverse),Nt.setFromProjectionMatrix(Xt,zi,X.reversedDepth),_t=this.localClippingEnabled,Mt=Qe.init(this.clippingPlanes,_t),L=Le.get(C,D.length),L.init(),D.push(L),He.enabled===!0&&He.isPresenting===!0){const ze=z.xr.getDepthSensingMesh();ze!==null&&As(ze,X,-1/0,z.sortObjects)}As(C,X,0,z.sortObjects),L.finish(),z.sortObjects===!0&&L.sort(Fe,Je,X.reversedDepth),It=He.enabled===!1||He.isPresenting===!1||He.hasDepthSensing()===!1,It&&at.addToRenderList(L,C),this.info.render.frame++,this.info.autoReset===!0&&this.info.reset(),Mt===!0&&Qe.beginShadows();const ee=R.state.shadowsArray;if(tt.render(ee,C,X),Mt===!0&&Qe.endShadows(),(te&&I.hasRenderPass())===!1){const ze=L.opaque,we=L.transmissive;if(R.setupLights(),X.isArrayCamera){const We=X.cameras;if(we.length>0)for(let Ze=0,lt=We.length;Ze<lt;Ze++){const ct=We[Ze];Do(ze,we,C,ct)}It&&at.render(C);for(let Ze=0,lt=We.length;Ze<lt;Ze++){const ct=We[Ze];Aa(L,C,ct,ct.viewport)}}else we.length>0&&Do(ze,we,C,X),It&&at.render(C),Aa(L,C,X)}q!==null&&K===0&&(de.updateMultisampleRenderTarget(q),de.updateRenderTargetMipmap(q)),te&&I.end(z),C.isScene===!0&&C.onAfterRender(z,C,X),Ie.resetDefaultState(),se=-1,le=null,E.pop(),E.length>0?(R=E[E.length-1],de.setTextureUnits(R.state.textureUnits),Mt===!0&&Qe.setGlobalState(z.clippingPlanes,R.state.camera)):R=null,D.pop(),D.length>0?L=D[D.length-1]:L=null,H!==null&&H.renderEnd()};function As(C,X,ae,te){if(C.visible===!1)return;if(C.layers.test(X.layers)){if(C.isGroup)ae=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(X);else if(C.isLightProbeGrid)R.pushLightProbeGrid(C);else if(C.isLight)R.pushLight(C),C.castShadow&&R.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||Nt.intersectsSprite(C)){te&&nn.setFromMatrixPosition(C.matrixWorld).applyMatrix4(Xt);const ze=ge.update(C),we=C.material;we.visible&&L.push(C,ze,we,ae,nn.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(!C.frustumCulled||Nt.intersectsObject(C))){const ze=ge.update(C),we=C.material;if(te&&(C.boundingSphere!==void 0?(C.boundingSphere===null&&C.computeBoundingSphere(),nn.copy(C.boundingSphere.center)):(ze.boundingSphere===null&&ze.computeBoundingSphere(),nn.copy(ze.boundingSphere.center)),nn.applyMatrix4(C.matrixWorld).applyMatrix4(Xt)),Array.isArray(we)){const We=ze.groups;for(let Ze=0,lt=We.length;Ze<lt;Ze++){const ct=We[Ze],Ye=we[ct.materialIndex];Ye&&Ye.visible&&L.push(C,ze,Ye,ae,nn.z,ct)}}else we.visible&&L.push(C,ze,we,ae,nn.z,null)}}const Te=C.children;for(let ze=0,we=Te.length;ze<we;ze++)As(Te[ze],X,ae,te)}function Aa(C,X,ae,te){const{opaque:ee,transmissive:Te,transparent:ze}=C;R.setupLightsView(ae),Mt===!0&&Qe.setGlobalState(z.clippingPlanes,ae),te&&b.viewport(k.copy(te)),ee.length>0&&Qr(ee,X,ae),Te.length>0&&Qr(Te,X,ae),ze.length>0&&Qr(ze,X,ae),b.buffers.depth.setTest(!0),b.buffers.depth.setMask(!0),b.buffers.color.setMask(!0),b.setPolygonOffset(!1)}function Do(C,X,ae,te){if((ae.isScene===!0?ae.overrideMaterial:null)!==null)return;if(R.state.transmissionRenderTarget[te.id]===void 0){const Ye=Tt.has("EXT_color_buffer_half_float")||Tt.has("EXT_color_buffer_float");R.state.transmissionRenderTarget[te.id]=new Vi(1,1,{generateMipmaps:!0,type:Ye?ur:pi,minFilter:ys,samples:Math.max(4,F.samples),stencilBuffer:l,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:St.workingColorSpace})}const Te=R.state.transmissionRenderTarget[te.id],ze=te.viewport||k;Te.setSize(ze.z*z.transmissionResolutionScale,ze.w*z.transmissionResolutionScale);const we=z.getRenderTarget(),We=z.getActiveCubeFace(),Ze=z.getActiveMipmapLevel();z.setRenderTarget(Te),z.getClearColor($e),Ve=z.getClearAlpha(),Ve<1&&z.setClearColor(16777215,.5),z.clear(),It&&at.render(ae);const lt=z.toneMapping;z.toneMapping=Bi;const ct=te.viewport;if(te.viewport!==void 0&&(te.viewport=void 0),R.setupLightsView(te),Mt===!0&&Qe.setGlobalState(z.clippingPlanes,te),Qr(C,ae,te),de.updateMultisampleRenderTarget(Te),de.updateRenderTargetMipmap(Te),Tt.has("WEBGL_multisampled_render_to_texture")===!1){let Ye=!1;for(let bt=0,Ot=X.length;bt<Ot;bt++){const Yt=X[bt],{object:Dt,geometry:on,material:ke,group:yn}=Yt;if(ke.side===sr&&Dt.layers.test(te.layers)){const mt=ke.side;ke.side=Zn,ke.needsUpdate=!0,Ca(Dt,ae,te,on,ke,yn),ke.side=mt,ke.needsUpdate=!0,Ye=!0}}Ye===!0&&(de.updateMultisampleRenderTarget(Te),de.updateRenderTargetMipmap(Te))}z.setRenderTarget(we,We,Ze),z.setClearColor($e,Ve),ct!==void 0&&(te.viewport=ct),z.toneMapping=lt}function Qr(C,X,ae){const te=X.isScene===!0?X.overrideMaterial:null;for(let ee=0,Te=C.length;ee<Te;ee++){const ze=C[ee],{object:we,geometry:We,group:Ze}=ze;let lt=ze.material;lt.allowOverride===!0&&te!==null&&(lt=te),we.layers.test(ae.layers)&&Ca(we,X,ae,We,lt,Ze)}}function Ca(C,X,ae,te,ee,Te){C.onBeforeRender(z,X,ae,te,ee,Te),C.modelViewMatrix.multiplyMatrices(ae.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),ee.onBeforeRender(z,X,ae,te,C,Te),ee.transparent===!0&&ee.side===sr&&ee.forceSinglePass===!1?(ee.side=Zn,ee.needsUpdate=!0,z.renderBufferDirect(ae,X,te,ee,C,Te),ee.side=Xr,ee.needsUpdate=!0,z.renderBufferDirect(ae,X,te,ee,C,Te),ee.side=sr):z.renderBufferDirect(ae,X,te,ee,C,Te),C.onAfterRender(z,X,ae,te,ee,Te)}function Jr(C,X,ae){X.isScene!==!0&&(X=Kt);const te=ie.get(C),ee=R.state.lights,Te=R.state.shadowsArray,ze=ee.state.version,we=Pe.getParameters(C,ee.state,Te,X,ae,R.state.lightProbeGridArray),We=Pe.getProgramCacheKey(we);let Ze=te.programs;te.environment=C.isMeshStandardMaterial||C.isMeshLambertMaterial||C.isMeshPhongMaterial?X.environment:null,te.fog=X.fog;const lt=C.isMeshStandardMaterial||C.isMeshLambertMaterial&&!C.envMap||C.isMeshPhongMaterial&&!C.envMap;te.envMap=be.get(C.envMap||te.environment,lt),te.envMapRotation=te.environment!==null&&C.envMap===null?X.environmentRotation:C.envMapRotation,Ze===void 0&&(C.addEventListener("dispose",ri),Ze=new Map,te.programs=Ze);let ct=Ze.get(We);if(ct!==void 0){if(te.currentProgram===ct&&te.lightsStateVersion===ze)return Uo(C,we),ct}else we.uniforms=Pe.getUniforms(C),H!==null&&C.isNodeMaterial&&H.build(C,ae,we),C.onBeforeCompile(we,z),ct=Pe.acquireProgram(we,We),Ze.set(We,ct),te.uniforms=we.uniforms;const Ye=te.uniforms;return(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(Ye.clippingPlanes=Qe.uniform),Uo(C,we),te.needsLights=Ra(C),te.lightsStateVersion=ze,te.needsLights&&(Ye.ambientLightColor.value=ee.state.ambient,Ye.lightProbe.value=ee.state.probe,Ye.directionalLights.value=ee.state.directional,Ye.directionalLightShadows.value=ee.state.directionalShadow,Ye.spotLights.value=ee.state.spot,Ye.spotLightShadows.value=ee.state.spotShadow,Ye.rectAreaLights.value=ee.state.rectArea,Ye.ltc_1.value=ee.state.rectAreaLTC1,Ye.ltc_2.value=ee.state.rectAreaLTC2,Ye.pointLights.value=ee.state.point,Ye.pointLightShadows.value=ee.state.pointShadow,Ye.hemisphereLights.value=ee.state.hemi,Ye.directionalShadowMatrix.value=ee.state.directionalShadowMatrix,Ye.spotLightMatrix.value=ee.state.spotLightMatrix,Ye.spotLightMap.value=ee.state.spotLightMap,Ye.pointShadowMatrix.value=ee.state.pointShadowMatrix),te.lightProbeGrid=R.state.lightProbeGridArray.length>0,te.currentProgram=ct,te.uniformsList=null,ct}function Na(C){if(C.uniformsList===null){const X=C.currentProgram.getUniforms();C.uniformsList=mc.seqWithValue(X.seq,C.uniforms)}return C.uniformsList}function Uo(C,X){const ae=ie.get(C);ae.outputColorSpace=X.outputColorSpace,ae.batching=X.batching,ae.batchingColor=X.batchingColor,ae.instancing=X.instancing,ae.instancingColor=X.instancingColor,ae.instancingMorph=X.instancingMorph,ae.skinning=X.skinning,ae.morphTargets=X.morphTargets,ae.morphNormals=X.morphNormals,ae.morphColors=X.morphColors,ae.morphTargetsCount=X.morphTargetsCount,ae.numClippingPlanes=X.numClippingPlanes,ae.numIntersection=X.numClipIntersection,ae.vertexAlphas=X.vertexAlphas,ae.vertexTangents=X.vertexTangents,ae.toneMapping=X.toneMapping}function kc(C,X){if(C.length===0)return null;if(C.length===1)return C[0].texture!==null?C[0]:null;N.setFromMatrixPosition(X.matrixWorld);for(let ae=0,te=C.length;ae<te;ae++){const ee=C[ae];if(ee.texture!==null&&ee.boundingBox.containsPoint(N))return ee}return null}function Zt(C,X,ae,te,ee){X.isScene!==!0&&(X=Kt),de.resetTextureUnits();const Te=X.fog,ze=te.isMeshStandardMaterial||te.isMeshLambertMaterial||te.isMeshPhongMaterial?X.environment:null,we=q===null?z.outputColorSpace:q.isXRRenderTarget===!0?q.texture.colorSpace:St.workingColorSpace,We=te.isMeshStandardMaterial||te.isMeshLambertMaterial&&!te.envMap||te.isMeshPhongMaterial&&!te.envMap,Ze=be.get(te.envMap||ze,We),lt=te.vertexColors===!0&&!!ae.attributes.color&&ae.attributes.color.itemSize===4,ct=!!ae.attributes.tangent&&(!!te.normalMap||te.anisotropy>0),Ye=!!ae.morphAttributes.position,bt=!!ae.morphAttributes.normal,Ot=!!ae.morphAttributes.color;let Yt=Bi;te.toneMapped&&(q===null||q.isXRRenderTarget===!0)&&(Yt=z.toneMapping);const Dt=ae.morphAttributes.position||ae.morphAttributes.normal||ae.morphAttributes.color,on=Dt!==void 0?Dt.length:0,ke=ie.get(te),yn=R.state.lights;if(Mt===!0&&(_t===!0||C!==le)){const Ut=C===le&&te.id===se;Qe.setState(te,C,Ut)}let mt=!1;te.version===ke.__version?(ke.needsLights&&ke.lightsStateVersion!==yn.state.version||ke.outputColorSpace!==we||ee.isBatchedMesh&&ke.batching===!1||!ee.isBatchedMesh&&ke.batching===!0||ee.isBatchedMesh&&ke.batchingColor===!0&&ee.colorTexture===null||ee.isBatchedMesh&&ke.batchingColor===!1&&ee.colorTexture!==null||ee.isInstancedMesh&&ke.instancing===!1||!ee.isInstancedMesh&&ke.instancing===!0||ee.isSkinnedMesh&&ke.skinning===!1||!ee.isSkinnedMesh&&ke.skinning===!0||ee.isInstancedMesh&&ke.instancingColor===!0&&ee.instanceColor===null||ee.isInstancedMesh&&ke.instancingColor===!1&&ee.instanceColor!==null||ee.isInstancedMesh&&ke.instancingMorph===!0&&ee.morphTexture===null||ee.isInstancedMesh&&ke.instancingMorph===!1&&ee.morphTexture!==null||ke.envMap!==Ze||te.fog===!0&&ke.fog!==Te||ke.numClippingPlanes!==void 0&&(ke.numClippingPlanes!==Qe.numPlanes||ke.numIntersection!==Qe.numIntersection)||ke.vertexAlphas!==lt||ke.vertexTangents!==ct||ke.morphTargets!==Ye||ke.morphNormals!==bt||ke.morphColors!==Ot||ke.toneMapping!==Yt||ke.morphTargetsCount!==on||!!ke.lightProbeGrid!=R.state.lightProbeGridArray.length>0)&&(mt=!0):(mt=!0,ke.__version=te.version);let Hn=ke.currentProgram;mt===!0&&(Hn=Jr(te,X,ee),H&&te.isNodeMaterial&&H.onUpdateProgram(te,Hn,ke));let jn=!1,gt=!1,Gi=!1;const Pt=Hn.getUniforms(),Vt=ke.uniforms;if(b.useProgram(Hn.program)&&(jn=!0,gt=!0,Gi=!0),te.id!==se&&(se=te.id,gt=!0),ke.needsLights){const Ut=kc(R.state.lightProbeGridArray,ee);ke.lightProbeGrid!==Ut&&(ke.lightProbeGrid=Ut,gt=!0)}if(jn||le!==C){b.buffers.depth.getReversed()&&C.reversedDepth!==!0&&(C._reversedDepth=!0,C.updateProjectionMatrix()),Pt.setValue(W,"projectionMatrix",C.projectionMatrix),Pt.setValue(W,"viewMatrix",C.matrixWorldInverse);const xi=Pt.map.cameraPosition;xi!==void 0&&xi.setValue(W,tn.setFromMatrixPosition(C.matrixWorld)),F.logarithmicDepthBuffer&&Pt.setValue(W,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),(te.isMeshPhongMaterial||te.isMeshToonMaterial||te.isMeshLambertMaterial||te.isMeshBasicMaterial||te.isMeshStandardMaterial||te.isShaderMaterial)&&Pt.setValue(W,"isOrthographic",C.isOrthographicCamera===!0),le!==C&&(le=C,gt=!0,Gi=!0)}if(ke.needsLights&&(yn.state.directionalShadowMap.length>0&&Pt.setValue(W,"directionalShadowMap",yn.state.directionalShadowMap,de),yn.state.spotShadowMap.length>0&&Pt.setValue(W,"spotShadowMap",yn.state.spotShadowMap,de),yn.state.pointShadowMap.length>0&&Pt.setValue(W,"pointShadowMap",yn.state.pointShadowMap,de)),ee.isSkinnedMesh){Pt.setOptional(W,ee,"bindMatrix"),Pt.setOptional(W,ee,"bindMatrixInverse");const Ut=ee.skeleton;Ut&&(Ut.boneTexture===null&&Ut.computeBoneTexture(),Pt.setValue(W,"boneTexture",Ut.boneTexture,de))}ee.isBatchedMesh&&(Pt.setOptional(W,ee,"batchingTexture"),Pt.setValue(W,"batchingTexture",ee._matricesTexture,de),Pt.setOptional(W,ee,"batchingIdTexture"),Pt.setValue(W,"batchingIdTexture",ee._indirectTexture,de),Pt.setOptional(W,ee,"batchingColorTexture"),ee._colorsTexture!==null&&Pt.setValue(W,"batchingColorTexture",ee._colorsTexture,de));const gi=ae.morphAttributes;if((gi.position!==void 0||gi.normal!==void 0||gi.color!==void 0)&&j.update(ee,ae,Hn),(gt||ke.receiveShadow!==ee.receiveShadow)&&(ke.receiveShadow=ee.receiveShadow,Pt.setValue(W,"receiveShadow",ee.receiveShadow)),(te.isMeshStandardMaterial||te.isMeshLambertMaterial||te.isMeshPhongMaterial)&&te.envMap===null&&X.environment!==null&&(Vt.envMapIntensity.value=X.environmentIntensity),Vt.dfgLUT!==void 0&&(Vt.dfgLUT.value=hT()),gt){if(Pt.setValue(W,"toneMappingExposure",z.toneMappingExposure),ke.needsLights&&Oc(Vt,Gi),Te&&te.fog===!0&&qe.refreshFogUniforms(Vt,Te),qe.refreshMaterialUniforms(Vt,te,me,_e,R.state.transmissionRenderTarget[C.id]),ke.needsLights&&ke.lightProbeGrid){const Ut=ke.lightProbeGrid;Vt.probesSH.value=Ut.texture,Vt.probesMin.value.copy(Ut.boundingBox.min),Vt.probesMax.value.copy(Ut.boundingBox.max),Vt.probesResolution.value.copy(Ut.resolution)}mc.upload(W,Na(ke),Vt,de)}if(te.isShaderMaterial&&te.uniformsNeedUpdate===!0&&(mc.upload(W,Na(ke),Vt,de),te.uniformsNeedUpdate=!1),te.isSpriteMaterial&&Pt.setValue(W,"center",ee.center),Pt.setValue(W,"modelViewMatrix",ee.modelViewMatrix),Pt.setValue(W,"normalMatrix",ee.normalMatrix),Pt.setValue(W,"modelMatrix",ee.matrixWorld),te.uniformsGroups!==void 0){const Ut=te.uniformsGroups;for(let xi=0,Ri=Ut.length;xi<Ri;xi++){const es=Ut[xi];ve.update(es,Hn),ve.bind(es,Hn)}}return Hn}function Oc(C,X){C.ambientLightColor.needsUpdate=X,C.lightProbe.needsUpdate=X,C.directionalLights.needsUpdate=X,C.directionalLightShadows.needsUpdate=X,C.pointLights.needsUpdate=X,C.pointLightShadows.needsUpdate=X,C.spotLights.needsUpdate=X,C.spotLightShadows.needsUpdate=X,C.rectAreaLights.needsUpdate=X,C.hemisphereLights.needsUpdate=X}function Ra(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}this.getActiveCubeFace=function(){return ue},this.getActiveMipmapLevel=function(){return K},this.getRenderTarget=function(){return q},this.setRenderTargetTextures=function(C,X,ae){const te=ie.get(C);te.__autoAllocateDepthBuffer=C.resolveDepthBuffer===!1,te.__autoAllocateDepthBuffer===!1&&(te.__useRenderToTexture=!1),ie.get(C.texture).__webglTexture=X,ie.get(C.depthTexture).__webglTexture=te.__autoAllocateDepthBuffer?void 0:ae,te.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(C,X){const ae=ie.get(C);ae.__webglFramebuffer=X,ae.__useDefaultFramebuffer=X===void 0},this.setRenderTarget=function(C,X=0,ae=0){q=C,ue=X,K=ae;let te=null,ee=!1,Te=!1;if(C){const we=ie.get(C);if(we.__useDefaultFramebuffer!==void 0){b.bindFramebuffer(W.FRAMEBUFFER,we.__webglFramebuffer),k.copy(C.viewport),Q.copy(C.scissor),Ue=C.scissorTest,b.viewport(k),b.scissor(Q),b.setScissorTest(Ue),se=-1;return}else if(we.__webglFramebuffer===void 0)de.setupRenderTarget(C);else if(we.__hasExternalTextures)de.rebindTextures(C,ie.get(C.texture).__webglTexture,ie.get(C.depthTexture).__webglTexture);else if(C.depthBuffer){const lt=C.depthTexture;if(we.__boundDepthTexture!==lt){if(lt!==null&&ie.has(lt)&&(C.width!==lt.image.width||C.height!==lt.image.height))throw new Error("THREE.WebGLRenderer: Attached DepthTexture is initialized to the incorrect size.");de.setupDepthRenderbuffer(C)}}const We=C.texture;(We.isData3DTexture||We.isDataArrayTexture||We.isCompressedArrayTexture)&&(Te=!0);const Ze=ie.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Array.isArray(Ze[X])?te=Ze[X][ae]:te=Ze[X],ee=!0):C.samples>0&&de.useMultisampledRTT(C)===!1?te=ie.get(C).__webglMultisampledFramebuffer:Array.isArray(Ze)?te=Ze[ae]:te=Ze,k.copy(C.viewport),Q.copy(C.scissor),Ue=C.scissorTest}else k.copy(et).multiplyScalar(me).floor(),Q.copy(Wt).multiplyScalar(me).floor(),Ue=ft;if(ae!==0&&(te=ce),b.bindFramebuffer(W.FRAMEBUFFER,te)&&b.drawBuffers(C,te),b.viewport(k),b.scissor(Q),b.setScissorTest(Ue),ee){const we=ie.get(C.texture);W.framebufferTexture2D(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_CUBE_MAP_POSITIVE_X+X,we.__webglTexture,ae)}else if(Te){const we=X;for(let We=0;We<C.textures.length;We++){const Ze=ie.get(C.textures[We]);W.framebufferTextureLayer(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0+We,Ze.__webglTexture,ae,we)}}else if(C!==null&&ae!==0){const we=ie.get(C.texture);W.framebufferTexture2D(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_2D,we.__webglTexture,ae)}se=-1},this.readRenderTargetPixels=function(C,X,ae,te,ee,Te,ze,we=0){if(!(C&&C.isWebGLRenderTarget)){wt("WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let We=ie.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&ze!==void 0&&(We=We[ze]),We){b.bindFramebuffer(W.FRAMEBUFFER,We);try{const Ze=C.textures[we],lt=Ze.format,ct=Ze.type;if(C.textures.length>1&&W.readBuffer(W.COLOR_ATTACHMENT0+we),!F.textureFormatReadable(lt)){wt("WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!F.textureTypeReadable(ct)){wt("WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}X>=0&&X<=C.width-te&&ae>=0&&ae<=C.height-ee&&W.readPixels(X,ae,te,ee,Re.convert(lt),Re.convert(ct),Te)}finally{const Ze=q!==null?ie.get(q).__webglFramebuffer:null;b.bindFramebuffer(W.FRAMEBUFFER,Ze)}}},this.readRenderTargetPixelsAsync=async function(C,X,ae,te,ee,Te,ze,we=0){if(!(C&&C.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let We=ie.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&ze!==void 0&&(We=We[ze]),We)if(X>=0&&X<=C.width-te&&ae>=0&&ae<=C.height-ee){b.bindFramebuffer(W.FRAMEBUFFER,We);const Ze=C.textures[we],lt=Ze.format,ct=Ze.type;if(C.textures.length>1&&W.readBuffer(W.COLOR_ATTACHMENT0+we),!F.textureFormatReadable(lt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!F.textureTypeReadable(ct))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");const Ye=W.createBuffer();W.bindBuffer(W.PIXEL_PACK_BUFFER,Ye),W.bufferData(W.PIXEL_PACK_BUFFER,Te.byteLength,W.STREAM_READ),W.readPixels(X,ae,te,ee,Re.convert(lt),Re.convert(ct),0);const bt=q!==null?ie.get(q).__webglFramebuffer:null;b.bindFramebuffer(W.FRAMEBUFFER,bt);const Ot=W.fenceSync(W.SYNC_GPU_COMMANDS_COMPLETE,0);return W.flush(),await PS(W,Ot,4),W.bindBuffer(W.PIXEL_PACK_BUFFER,Ye),W.getBufferSubData(W.PIXEL_PACK_BUFFER,0,Te),W.deleteBuffer(Ye),W.deleteSync(Ot),Te}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")},this.copyFramebufferToTexture=function(C,X=null,ae=0){const te=Math.pow(2,-ae),ee=Math.floor(C.image.width*te),Te=Math.floor(C.image.height*te),ze=X!==null?X.x:0,we=X!==null?X.y:0;de.setTexture2D(C,0),W.copyTexSubImage2D(W.TEXTURE_2D,ae,0,0,ze,we,ee,Te),b.unbindTexture()},this.copyTextureToTexture=function(C,X,ae=null,te=null,ee=0,Te=0){let ze,we,We,Ze,lt,ct,Ye,bt,Ot;const Yt=C.isCompressedTexture?C.mipmaps[Te]:C.image;if(ae!==null)ze=ae.max.x-ae.min.x,we=ae.max.y-ae.min.y,We=ae.isBox3?ae.max.z-ae.min.z:1,Ze=ae.min.x,lt=ae.min.y,ct=ae.isBox3?ae.min.z:0;else{const Vt=Math.pow(2,-ee);ze=Math.floor(Yt.width*Vt),we=Math.floor(Yt.height*Vt),C.isDataArrayTexture?We=Yt.depth:C.isData3DTexture?We=Math.floor(Yt.depth*Vt):We=1,Ze=0,lt=0,ct=0}te!==null?(Ye=te.x,bt=te.y,Ot=te.z):(Ye=0,bt=0,Ot=0);const Dt=Re.convert(X.format),on=Re.convert(X.type);let ke;X.isData3DTexture?(de.setTexture3D(X,0),ke=W.TEXTURE_3D):X.isDataArrayTexture||X.isCompressedArrayTexture?(de.setTexture2DArray(X,0),ke=W.TEXTURE_2D_ARRAY):(de.setTexture2D(X,0),ke=W.TEXTURE_2D),b.activeTexture(W.TEXTURE0),b.pixelStorei(W.UNPACK_FLIP_Y_WEBGL,X.flipY),b.pixelStorei(W.UNPACK_PREMULTIPLY_ALPHA_WEBGL,X.premultiplyAlpha),b.pixelStorei(W.UNPACK_ALIGNMENT,X.unpackAlignment);const yn=b.getParameter(W.UNPACK_ROW_LENGTH),mt=b.getParameter(W.UNPACK_IMAGE_HEIGHT),Hn=b.getParameter(W.UNPACK_SKIP_PIXELS),jn=b.getParameter(W.UNPACK_SKIP_ROWS),gt=b.getParameter(W.UNPACK_SKIP_IMAGES);b.pixelStorei(W.UNPACK_ROW_LENGTH,Yt.width),b.pixelStorei(W.UNPACK_IMAGE_HEIGHT,Yt.height),b.pixelStorei(W.UNPACK_SKIP_PIXELS,Ze),b.pixelStorei(W.UNPACK_SKIP_ROWS,lt),b.pixelStorei(W.UNPACK_SKIP_IMAGES,ct);const Gi=C.isDataArrayTexture||C.isData3DTexture,Pt=X.isDataArrayTexture||X.isData3DTexture;if(C.isDepthTexture){const Vt=ie.get(C),gi=ie.get(X),Ut=ie.get(Vt.__renderTarget),xi=ie.get(gi.__renderTarget);b.bindFramebuffer(W.READ_FRAMEBUFFER,Ut.__webglFramebuffer),b.bindFramebuffer(W.DRAW_FRAMEBUFFER,xi.__webglFramebuffer);for(let Ri=0;Ri<We;Ri++)Gi&&(W.framebufferTextureLayer(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,ie.get(C).__webglTexture,ee,ct+Ri),W.framebufferTextureLayer(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,ie.get(X).__webglTexture,Te,Ot+Ri)),W.blitFramebuffer(Ze,lt,ze,we,Ye,bt,ze,we,W.DEPTH_BUFFER_BIT,W.NEAREST);b.bindFramebuffer(W.READ_FRAMEBUFFER,null),b.bindFramebuffer(W.DRAW_FRAMEBUFFER,null)}else if(ee!==0||C.isRenderTargetTexture||ie.has(C)){const Vt=ie.get(C),gi=ie.get(X);b.bindFramebuffer(W.READ_FRAMEBUFFER,he),b.bindFramebuffer(W.DRAW_FRAMEBUFFER,Z);for(let Ut=0;Ut<We;Ut++)Gi?W.framebufferTextureLayer(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,Vt.__webglTexture,ee,ct+Ut):W.framebufferTexture2D(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_2D,Vt.__webglTexture,ee),Pt?W.framebufferTextureLayer(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,gi.__webglTexture,Te,Ot+Ut):W.framebufferTexture2D(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_2D,gi.__webglTexture,Te),ee!==0?W.blitFramebuffer(Ze,lt,ze,we,Ye,bt,ze,we,W.COLOR_BUFFER_BIT,W.NEAREST):Pt?W.copyTexSubImage3D(ke,Te,Ye,bt,Ot+Ut,Ze,lt,ze,we):W.copyTexSubImage2D(ke,Te,Ye,bt,Ze,lt,ze,we);b.bindFramebuffer(W.READ_FRAMEBUFFER,null),b.bindFramebuffer(W.DRAW_FRAMEBUFFER,null)}else Pt?C.isDataTexture||C.isData3DTexture?W.texSubImage3D(ke,Te,Ye,bt,Ot,ze,we,We,Dt,on,Yt.data):X.isCompressedArrayTexture?W.compressedTexSubImage3D(ke,Te,Ye,bt,Ot,ze,we,We,Dt,Yt.data):W.texSubImage3D(ke,Te,Ye,bt,Ot,ze,we,We,Dt,on,Yt):C.isDataTexture?W.texSubImage2D(W.TEXTURE_2D,Te,Ye,bt,ze,we,Dt,on,Yt.data):C.isCompressedTexture?W.compressedTexSubImage2D(W.TEXTURE_2D,Te,Ye,bt,Yt.width,Yt.height,Dt,Yt.data):W.texSubImage2D(W.TEXTURE_2D,Te,Ye,bt,ze,we,Dt,on,Yt);b.pixelStorei(W.UNPACK_ROW_LENGTH,yn),b.pixelStorei(W.UNPACK_IMAGE_HEIGHT,mt),b.pixelStorei(W.UNPACK_SKIP_PIXELS,Hn),b.pixelStorei(W.UNPACK_SKIP_ROWS,jn),b.pixelStorei(W.UNPACK_SKIP_IMAGES,gt),Te===0&&X.generateMipmaps&&W.generateMipmap(ke),b.unbindTexture()},this.initRenderTarget=function(C){ie.get(C).__webglFramebuffer===void 0&&de.setupRenderTarget(C)},this.initTexture=function(C){C.isCubeTexture?de.setTextureCube(C,0):C.isData3DTexture?de.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?de.setTexture2DArray(C,0):de.setTexture2D(C,0),b.unbindTexture()},this.resetState=function(){ue=0,K=0,q=null,b.reset(),Ie.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return zi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=St._getDrawingBufferColorSpace(e),t.unpackColorSpace=St._getUnpackColorSpace()}}const mT=()=>{const s=xe.useRef(null);return xe.useEffect(()=>{const e=s.current;if(!e||!window.WebGLRenderingContext&&!window.WebGL2RenderingContext||!(e.getContext("webgl2")||e.getContext("webgl")))return;let r;try{r=new pT({canvas:e,alpha:!0,antialias:!0})}catch{return}r.setPixelRatio(Math.min(window.devicePixelRatio,2));const o=new qS,l=new hi(40,1,.1,100);l.position.set(0,0,8);const d=new Mo;o.add(d);const f=new mi(new Ac(1.03,3),new Eo({color:"#6ee7b7",wireframe:!0,transparent:!0,opacity:.9}));d.add(f);const p=new mi(new Ac(.78,2),new Eo({color:"#d1fae5",transparent:!0,opacity:.1}));d.add(p);const m=new zx({color:"#34d399",transparent:!0,opacity:.42}),_=[];[{radius:2,tilt:.55,phase:0},{radius:2.55,tilt:-.7,phase:1.7},{radius:3.1,tilt:.12,phase:3.6}].forEach(({radius:R,tilt:D,phase:E},I)=>{const B=new l1(0,0,R,R*.34,0,Math.PI*2,!1,0).getPoints(80).map(he=>new Y(he.x,he.y,0)),H=new r1(new Vn().setFromPoints(B),m);H.rotation.x=D,H.rotation.z=I*.72,d.add(H);const ce=new mi(new ph(.1,16,16),new Eo({color:I===1?"#6ee7b7":"#f8fafc"}));ce.userData={radius:R,tilt:D,phase:E,rotationZ:I*.72,speed:.42+I*.08},d.add(ce),_.push(ce)});const S=new Vn,x=new Float32Array(180);for(let R=0;R<x.length;R+=3)x[R]=(Math.random()-.5)*9,x[R+1]=(Math.random()-.5)*7,x[R+2]=(Math.random()-.5)*4-1;S.setAttribute("position",new Ni(x,3));const M=new s1(S,new Bx({color:"#6ee7b7",size:.035,transparent:!0,opacity:.58}));o.add(M);let w=0,A=0,v=0;const y=R=>{w=(R.clientX/window.innerWidth-.5)*.45,A=(R.clientY/window.innerHeight-.5)*.25};window.addEventListener("pointermove",y,{passive:!0});const P=()=>{const{width:R,height:D}=e.getBoundingClientRect();R===0||D===0||(r.setSize(R,D,!1),l.aspect=R/D,l.updateProjectionMatrix())},U=new ResizeObserver(P);U.observe(e),P();const N=new v1,L=()=>{const R=N.getElapsedTime();d.rotation.y+=(w-d.rotation.y)*.025,d.rotation.x+=(A-d.rotation.x)*.025,f.rotation.x=R*.18,f.rotation.z=R*.12,p.scale.setScalar(1+Math.sin(R*1.5)*.04),M.rotation.z=R*.018,_.forEach(D=>{const{radius:E,tilt:I,phase:z,rotationZ:B,speed:H}=D.userData,ce=R*H+z;D.position.set(E*Math.cos(ce),E*.34*Math.sin(ce),0),D.position.applyAxisAngle(new Y(1,0,0),I),D.position.applyAxisAngle(new Y(0,0,1),B)}),r.render(o,l),v=window.requestAnimationFrame(L)};return L(),()=>{window.cancelAnimationFrame(v),window.removeEventListener("pointermove",y),U.disconnect(),f.geometry.dispose(),f.material.dispose(),p.geometry.dispose(),p.material.dispose(),_.forEach(R=>{R.geometry.dispose(),R.material.dispose()}),S.dispose(),M.material.dispose(),m.dispose(),r.dispose()}},[]),u.jsxs("div",{className:"absolute inset-y-0 right-0 hidden w-[54%] overflow-hidden lg:block","aria-hidden":"true",children:[u.jsx("div",{className:"absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.13),transparent_58%)]"}),u.jsx("canvas",{ref:s,className:"h-full w-full"})]})},tf=({children:s,className:e=""})=>{const t=xe.useRef(null),[r,o]=xe.useState(!1);return xe.useEffect(()=>{const l=t.current;if(!l)return;if(typeof window<"u"&&typeof window.matchMedia=="function"&&window.matchMedia("(prefers-reduced-motion: reduce)").matches){o(!0);return}if(typeof IntersectionObserver>"u"){o(!0);return}const d=new IntersectionObserver(([f])=>{f.isIntersecting&&(o(!0),d.disconnect())},{rootMargin:"0px 0px -8% 0px",threshold:.12});return d.observe(l),()=>d.disconnect()},[]),u.jsx("div",{ref:t,className:`scroll-reveal ${r?"scroll-reveal-visible":""} ${e}`,children:s})},gT=({onNavigate:s})=>{const[e,t]=xe.useState(0),r=[{id:0,badge:"Step 1: Inbound Discovery",title:"Untrusted Buyer Agent",desc:"Autonomous buyer agents discover products, negotiate quotes, and submit structured commerce intents under strict token constraints.",invariant:"INV-AGY-01: Separation of Intelligence & Authority",details:"All LLM proposals are wrapped in typed schemas and treated as completely untrusted input.",color:"from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-300"},{id:1,badge:"Step 2: Deterministic Governance",title:"Policy Engine Validation",desc:"Pre-flight mathematical checks verify floor price margin, discount ceilings, max items, and merchant autonomy rules before any mutation.",invariant:"INV-FIN-02: Strict Merchant Floor Price Guarantee",details:"Evaluates ALLOW, ESCALATE_APPROVAL, or DENY with zero possibility of LLM override.",color:"from-brand/20 to-emerald-500/20 border-brand/40 text-brand-bright"},{id:2,badge:"Step 3: Human-In-The-Loop",title:"HITL Approval Queue",desc:"High-discount negotiations or abnormal buyer proposals are escalated into expiring decision tickets for merchant review.",invariant:"INV-AGY-02: Capability Boundary Enforcement",details:"Optimistic concurrency locking ensures tickets cannot be double-resolved or bypassed.",color:"from-amber-500/20 to-orange-500/20 border-amber-500/40 text-amber-400"},{id:3,badge:"Step 4: Financial Settlement",title:"Razorpay Gateway & Webhooks",desc:"Idempotent order generation and server-authoritative HMAC SHA-256 webhook capture guarantee exact 64-bit integer paise settlement.",invariant:"INV-FIN-01 & INV-FIN-05: Server-Authoritative Settlement",details:"Webhooks are deduplicated durably; stock is deducted atomically upon verified payment.",color:"from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-400"},{id:4,badge:"Step 5: Cryptographic Assurance",title:"Immutable SHA-256 Audit Trail",desc:"Every session, quote, policy decision, approval, and settlement is chained with SHA-256 hashes for instant tamper detection.",invariant:"INV-AGY-04: Tamper-Evident Cryptographic Ledger",details:"Any out-of-band database mutation breaks the cryptographic link and alerts operators.",color:"from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-300"}];return u.jsxs("div",{className:"landing-theme flex min-h-screen flex-col overflow-hidden bg-[#080c0b] text-[#f8fafc] selection:bg-emerald-300/30",children:[u.jsxs("section",{className:"relative isolate overflow-hidden border-b border-white/[0.07] bg-[#080c0b] pb-20 pt-16 lg:pb-28 lg:pt-24",children:[u.jsx("div",{className:"hero-grid absolute inset-0 -z-20 opacity-70"}),u.jsx("div",{className:"absolute -left-28 top-0 -z-10 h-[34rem] w-[34rem] rounded-full bg-emerald-400/[0.08] blur-[130px]"}),u.jsx("div",{className:"absolute bottom-0 right-[12%] -z-10 h-72 w-72 rounded-full bg-emerald-300/[0.06] blur-[110px]"}),u.jsx(mT,{}),u.jsxs("div",{className:"container relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8",children:[u.jsxs("div",{className:"max-w-3xl text-left",children:[u.jsxs("div",{className:"mb-8 inline-flex items-center gap-2 rounded-full border border-emerald-300/20 bg-slate-950/50 px-3.5 py-1.5 backdrop-blur",children:[u.jsx("span",{className:"h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_10px_#6ee7b7]"}),u.jsx("span",{className:"text-[10px] font-mono uppercase tracking-[0.16em] text-slate-300",children:"Agent commerce, constrained by design"})]}),u.jsxs("h1",{className:"max-w-3xl font-display text-5xl font-bold tracking-[-0.065em] text-slate-50 sm:text-6xl lg:text-7xl lg:leading-[0.98]",children:["The Autonomous AI Commerce"," ",u.jsx("span",{className:"text-emerald-300",children:"control layer"})," for merchants who mean business."]}),u.jsx("p",{className:"mt-7 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg",children:"pimp gives AI agents a governed way to buy from your store—with immutable policy, human escalation, and settlement that is verified before it moves a single paise."}),u.jsxs("div",{className:"mt-9 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center",children:[u.jsxs(dt,{onClick:()=>s("/signup"),size:"lg",className:"w-full rounded-xl bg-emerald-300 px-7 py-3 text-sm font-bold text-slate-950 shadow-[0_12px_40px_rgba(52,211,153,0.16)] hover:bg-emerald-200 sm:w-auto",children:["Build your control plane",u.jsx(cr,{className:"h-4 w-4 ml-2"})]}),u.jsxs(dt,{onClick:()=>s("/demo"),variant:"outline",size:"lg",className:"w-full rounded-xl border-slate-600/70 bg-slate-950/30 px-6 py-3 text-sm font-medium text-slate-100 hover:border-emerald-300/60 hover:bg-slate-900/80 sm:w-auto",children:[u.jsx(by,{className:"h-4 w-4 mr-2 text-emerald-300"}),"Explore the sandbox"]})]}),u.jsx("div",{className:"mt-12 flex flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-slate-300",children:["No below-floor pricing","Human approval when it matters","HMAC-verified settlement"].map(o=>u.jsxs("span",{className:"inline-flex items-center gap-1.5",children:[u.jsx(Jf,{className:"h-3.5 w-3.5 text-emerald-300"}),o]},o))})]}),u.jsxs("div",{className:"relative mt-16 grid max-w-5xl grid-cols-2 gap-3 lg:mt-20 lg:grid-cols-4",children:[u.jsxs("div",{className:"hero-proof-card p-3.5 rounded-2xl text-left",children:[u.jsxs("div",{className:"flex items-center gap-2 mb-1",children:[u.jsx(xc,{className:"h-4 w-4 text-emerald-300"}),u.jsx("span",{className:"text-[11px] font-mono font-bold text-slate-100",children:"INV-FIN-02"})]}),u.jsx("p",{className:"text-xs text-slate-400",children:"Strict floor price margin guarantee"})]}),u.jsxs("div",{className:"hero-proof-card p-3.5 rounded-2xl text-left",children:[u.jsxs("div",{className:"flex items-center gap-2 mb-1",children:[u.jsx(dx,{className:"h-4 w-4 text-emerald-300"}),u.jsx("span",{className:"text-[11px] font-mono font-bold text-slate-100",children:"INV-FIN-01"})]}),u.jsx("p",{className:"text-xs text-slate-400",children:"64-bit integer paise, never float math"})]}),u.jsxs("div",{className:"hero-proof-card p-3.5 rounded-2xl text-left",children:[u.jsxs("div",{className:"flex items-center gap-2 mb-1",children:[u.jsx(ox,{className:"h-4 w-4 text-violet-300"}),u.jsx("span",{className:"text-[11px] font-mono font-bold text-slate-100",children:"INV-AGY-01"})]}),u.jsx("p",{className:"text-xs text-slate-400",children:"Intelligence is never authority"})]}),u.jsxs("div",{className:"hero-proof-card p-3.5 rounded-2xl text-left",children:[u.jsxs("div",{className:"flex items-center gap-2 mb-1",children:[u.jsx(ey,{className:"h-4 w-4 text-emerald-300"}),u.jsx("span",{className:"text-[11px] font-mono font-bold text-slate-100",children:"INV-AGY-04"})]}),u.jsx("p",{className:"text-xs text-slate-400",children:"Immutable SHA-256 audit chain"})]})]})]})]}),u.jsx("section",{className:"py-20 border-t border-[#24314A]/80 bg-[#0D1424]/40 relative",children:u.jsxs("div",{className:"container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8",children:[u.jsxs("div",{className:"text-center max-w-3xl mx-auto mb-12",children:[u.jsx("span",{className:"text-xs font-mono font-semibold tracking-wider text-brand-bright uppercase",children:"System Architecture"}),u.jsx("h2",{className:"text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mt-2",children:"Server-Authoritative Agent Commerce Pipeline"}),u.jsx("p",{className:"mt-3 text-sm text-text-secondary",children:"Click any node in the pipeline to inspect its deterministic safety boundaries and security invariants."})]}),u.jsx("div",{className:"grid grid-cols-2 sm:grid-cols-5 gap-2 mb-8",children:r.map(o=>{const l=e===o.id;return u.jsxs("button",{onClick:()=>t(o.id),className:`p-3 rounded-xl text-left transition-all border ${l?"bg-[#141D31] border-brand shadow-glow-sm scale-[1.02]":"bg-[#0D1424]/80 border-[#24314A] hover:border-brand/40 opacity-75 hover:opacity-100"}`,children:[u.jsx("span",{className:"text-[10px] font-mono text-text-muted block",children:o.badge}),u.jsx("span",{className:"font-semibold text-xs text-text-primary block mt-0.5 truncate",children:o.title})]},o.id)})}),u.jsx("div",{className:"glass-panel rounded-2xl p-6 sm:p-8 border border-[#24314A] bg-[#0D1424]/90 relative overflow-hidden",children:u.jsxs("div",{className:"grid grid-cols-1 lg:grid-cols-3 gap-6 items-center",children:[u.jsxs("div",{className:"lg:col-span-2 space-y-3",children:[u.jsxs("div",{className:"inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-brand/10 border border-brand/30 text-brand-bright text-xs font-mono",children:[u.jsx(cy,{className:"h-3.5 w-3.5"}),r[e].invariant]}),u.jsx("h3",{className:"text-xl font-bold text-text-primary",children:r[e].title}),u.jsx("p",{className:"text-sm text-text-secondary leading-relaxed",children:r[e].desc}),u.jsxs("div",{className:"p-3.5 rounded-xl bg-[#070B14] border border-[#24314A] font-mono text-xs text-text-secondary",children:[u.jsx("span",{className:"text-emerald-400 font-bold block mb-1",children:"Server Guarantee:"}),r[e].details]})]}),u.jsxs("div",{className:"p-5 rounded-xl bg-[#070B14]/80 border border-[#24314A] space-y-3",children:[u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted",children:[u.jsx("span",{children:"Engine Status"}),u.jsx("span",{className:"text-emerald-400",children:"ACTIVE"})]}),u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted",children:[u.jsx("span",{children:"Target Database"}),u.jsx("span",{className:"text-text-primary",children:"PostgreSQL"})]}),u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted",children:[u.jsx("span",{children:"Payment Gateway"}),u.jsx("span",{className:"text-brand-bright",children:"Razorpay v1"})]}),u.jsx(dt,{onClick:()=>s("/demo"),size:"sm",className:"w-full mt-2 bg-brand/15 hover:bg-brand/25 border border-brand/40 text-brand-bright text-xs",children:"Simulate in Sandbox"})]})]})})]})}),u.jsx("section",{className:"border-t border-white/[0.07] bg-[#0a0e11] py-24",children:u.jsx("div",{className:"mx-auto max-w-7xl px-4 sm:px-6 lg:px-8",children:u.jsxs(tf,{className:"grid items-center gap-12 lg:grid-cols-[0.82fr_1.18fr]",children:[u.jsxs("div",{children:[u.jsx("span",{className:"text-[10px] font-mono font-semibold uppercase tracking-[0.18em] text-emerald-300",children:"One operating view"}),u.jsx("h2",{className:"mt-4 max-w-lg font-display text-3xl font-semibold tracking-[-0.045em] text-slate-50 sm:text-4xl",children:"See the decision before it becomes a transaction."}),u.jsx("p",{className:"mt-5 max-w-lg text-sm leading-7 text-slate-400",children:"Follow buyer intent from discovery through policy evaluation, merchant approval, and verified settlement—without giving the agent authority it should not have."}),u.jsxs("div",{className:"mt-8 grid grid-cols-2 gap-5 border-t border-white/10 pt-6",children:[u.jsxs("div",{children:[u.jsx("p",{className:"font-display text-2xl font-semibold text-slate-100",children:"5"}),u.jsx("p",{className:"mt-1 text-xs text-slate-500",children:"bounded tool steps"})]}),u.jsxs("div",{children:[u.jsx("p",{className:"font-display text-2xl font-semibold text-slate-100",children:"15s"}),u.jsx("p",{className:"mt-1 text-xs text-slate-500",children:"maximum agent turn"})]})]})]}),u.jsxs("div",{className:"operations-preview",children:[u.jsxs("div",{className:"flex items-center justify-between border-b border-white/10 px-5 py-3.5",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx("span",{className:"h-2 w-2 rounded-full bg-emerald-300"}),u.jsx("span",{className:"text-xs font-medium text-slate-200",children:"Live commerce trace"})]}),u.jsx("span",{className:"rounded border border-white/10 px-2 py-1 font-mono text-[9px] text-slate-500",children:"REQ_8F21"})]}),u.jsx("div",{className:"divide-y divide-white/[0.07]",children:[["01","Buyer intent received","UNTRUSTED",Sy],["02","Floor and discount policy checked","ALLOWED",D_],["03","Inventory version locked","RESERVED",O_],["04","Settlement webhook verified","CAPTURED",qy]].map(([o,l,d,f])=>{const p=f;return u.jsxs("div",{className:"group flex items-center gap-4 px-5 py-4 transition-colors hover:bg-white/[0.025]",children:[u.jsx("span",{className:"font-mono text-[10px] text-slate-600",children:o}),u.jsx("span",{className:"flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-white/[0.025] text-slate-400",children:u.jsx(p,{className:"h-4 w-4"})}),u.jsx("span",{className:"min-w-0 flex-1 text-sm text-slate-300",children:l}),u.jsx("span",{className:"font-mono text-[9px] font-semibold tracking-[0.1em] text-emerald-300",children:d})]},o)})})]})]})})}),u.jsx("section",{className:"py-20 border-t border-[#24314A]/60",children:u.jsxs("div",{className:"container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8",children:[u.jsxs("div",{className:"text-center max-w-2xl mx-auto mb-16",children:[u.jsx("span",{className:"text-xs font-mono text-brand-bright uppercase tracking-wider",children:"Merchant Governance"}),u.jsx("h2",{className:"text-3xl font-bold tracking-tight text-text-primary mt-1",children:"Engineered for Complete Autonomous Reliability"}),u.jsx("p",{className:"mt-3 text-sm text-text-secondary",children:"Four fundamental architectural pillars ensuring autonomous commerce operates with zero financial risk."})]}),u.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5",children:[u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsx("div",{className:"h-10 w-10 rounded-xl bg-brand/10 text-brand-bright flex items-center justify-center mb-4",children:u.jsx(Y_,{className:"h-5 w-5"})}),u.jsx("h3",{className:"text-sm font-bold text-text-primary mb-1",children:"Agent Protocol Native"}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"Seamless support for autonomous buyer sessions, structured quote negotiations, and product discovery RPCs."})]}),u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsx("div",{className:"h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4",children:u.jsx(xc,{className:"h-5 w-5"})}),u.jsx("h3",{className:"text-sm font-bold text-text-primary mb-1",children:"Deterministic Policy"}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"Mathematical floor price guarantees, 50% max discount caps, and integer paise monetary precision."})]}),u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsx("div",{className:"h-10 w-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-4",children:u.jsx(Pc,{className:"h-5 w-5"})}),u.jsx("h3",{className:"text-sm font-bold text-text-primary mb-1",children:"HITL Approval Queue"}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"Expiring decision tickets for high-discount negotiations with optimistic concurrency locking."})]}),u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsx("div",{className:"h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-300 flex items-center justify-center mb-4",children:u.jsx(Ky,{className:"h-5 w-5"})}),u.jsx("h3",{className:"text-sm font-bold text-text-primary mb-1",children:"Razorpay Settlement"}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"HMAC SHA-256 verified webhooks, idempotent orders, and tamper-evident cryptographic audit ledger."})]})]})]})}),u.jsx("section",{className:"border-t border-white/[0.07] bg-[#080b0d] py-24",children:u.jsxs("div",{className:"mx-auto max-w-7xl px-4 sm:px-6 lg:px-8",children:[u.jsx(tf,{children:u.jsx("div",{className:"grid gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/10 sm:grid-cols-3",children:[["Integer paise","Precise money by default","No floating-point pricing anywhere in the transaction path."],["Fail closed","Ambiguity never ships","Invalid state, policy, or capability checks stop before mutation."],["Audit chained","Every decision has a history","SHA-256 links policy decisions, approvals, and settlement events."]].map(([o,l,d])=>u.jsxs("div",{className:"bg-[#0c1114] p-7 sm:p-8",children:[u.jsx("p",{className:"font-mono text-[9px] font-semibold uppercase tracking-[0.16em] text-emerald-300",children:o}),u.jsx("h3",{className:"mt-4 text-lg font-semibold tracking-[-0.025em] text-slate-100",children:l}),u.jsx("p",{className:"mt-3 text-sm leading-6 text-slate-500",children:d})]},o))})}),u.jsxs(tf,{className:"mt-20 flex flex-col items-start justify-between gap-8 border-t border-white/10 pt-12 sm:flex-row sm:items-end",children:[u.jsxs("div",{children:[u.jsx("p",{className:"text-[10px] font-mono uppercase tracking-[0.18em] text-emerald-300",children:"Ready when you are"}),u.jsx("h2",{className:"mt-3 max-w-2xl font-display text-3xl font-semibold tracking-[-0.045em] text-slate-50 sm:text-4xl",children:"Give agents access to commerce. Keep authority with the merchant."})]}),u.jsxs(dt,{onClick:()=>s("/signup"),size:"lg",className:"shrink-0 bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200",children:["Create your store ",u.jsx(cr,{className:"h-4 w-4"})]})]})]})})]})},Lt=Nc.forwardRef(({className:s,type:e="text",label:t,error:r,helperText:o,id:l,...d},f)=>{const p=l||(t?t.toLowerCase().replace(/\s+/g,"-"):void 0);return u.jsxs("div",{className:"w-full space-y-1.5",children:[t&&u.jsx("label",{htmlFor:p,className:"block text-xs font-medium text-muted-foreground",children:t}),u.jsx("input",{id:p,type:e,ref:f,className:En("flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors",r&&"border-destructive focus-visible:ring-destructive",s),...d}),r&&u.jsx("p",{className:"text-xs text-destructive font-medium",children:r}),o&&!r&&u.jsx("p",{className:"text-xs text-muted-foreground",children:o})]})});Lt.displayName="Input";const xT=({onNavigate:s})=>{const{login:e,isLoading:t}=pr(),[r,o]=xe.useState(""),[l,d]=xe.useState(""),[f,p]=xe.useState(null),m=async S=>{if(S.preventDefault(),!r){p("Please enter your merchant slug.");return}p(null);try{await e({slug:r.trim().toLowerCase(),rzpKeyId:l.trim()||void 0}),s("/dashboard")}catch(x){p(x instanceof Error?x.message:"Invalid credentials or store not found.")}},_=()=>{o("acme-shoes"),d("rzp_test_acme123")};return u.jsx("div",{className:"auth-page",children:u.jsxs("div",{className:"auth-shell",children:[u.jsx("main",{className:"auth-form-side",children:u.jsxs("div",{className:"auth-form-wrap auth-reveal",children:[u.jsxs("button",{type:"button",onClick:()=>s("/"),className:"auth-back",children:[u.jsx(Qf,{className:"h-4 w-4"})," Home"]}),u.jsx("div",{className:"mt-9",children:u.jsx("span",{className:"auth-brand",children:"pimp"})}),u.jsxs("div",{className:"mt-12",children:[u.jsx("h1",{className:"text-3xl font-semibold tracking-[-0.055em] text-slate-50",children:"Merchant Sign In"}),u.jsx("p",{className:"mt-3 text-sm text-slate-400",children:"Access your governed commerce workspace."})]}),u.jsxs("form",{onSubmit:m,className:"mt-8 space-y-5",children:[f&&u.jsxs("div",{className:"flex items-center gap-2 rounded-md border border-rose-400/25 bg-rose-400/10 p-3 text-xs font-medium text-rose-200",children:[u.jsx(gc,{className:"h-4 w-4 shrink-0"}),f]}),u.jsx(Lt,{className:"auth-input",label:"Store Slug",placeholder:"e.g. acme-shoes",value:r,onChange:S=>o(S.target.value),required:!0}),u.jsx(Lt,{className:"auth-input",label:"Razorpay Key ID (Optional)",placeholder:"rzp_test_...",value:l,onChange:S=>d(S.target.value)}),u.jsx(dt,{type:"button",onClick:_,variant:"ghost",size:"sm",className:"w-full text-xs text-slate-400 hover:bg-slate-800 hover:text-slate-100",children:"Quick fill demo store (acme-shoes)"}),u.jsxs(dt,{type:"submit",className:"mt-2 w-full rounded-md bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200",isLoading:t,children:["Sign In ",u.jsx(cr,{className:"h-4 w-4"})]})]}),u.jsxs("p",{className:"mt-8 text-center text-sm text-slate-400",children:["Don't have a store? ",u.jsx("button",{type:"button",onClick:()=>s("/signup"),className:"font-medium text-slate-100 hover:underline",children:"Sign Up Now"})]})]})}),u.jsxs("aside",{className:"auth-visual-side","aria-hidden":"true",children:[u.jsx("div",{className:"auth-dot-field"}),u.jsxs("div",{className:"auth-visual-copy",children:["Operate commerce with ",u.jsx("span",{children:"certainty."})]})]})]})})},vT=({onNavigate:s})=>{const{signup:e,isLoading:t}=pr(),[r,o]=xe.useState(""),[l,d]=xe.useState(""),[f,p]=xe.useState(""),[m,_]=xe.useState("rzp_test_key_123"),[S,x]=xe.useState(null),M=A=>{const v=A.target.value;o(v),(!l||l===r.toLowerCase().replace(/[^a-z0-9]+/g,"-"))&&d(v.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""))},w=async A=>{if(A.preventDefault(),!r||!l||!f){x("Please fill in all required fields.");return}x(null);try{await e({name:r.trim(),slug:l.trim().toLowerCase(),email:f.trim(),rzpKeyId:m.trim()||"rzp_test_placeholder"}),s("/onboarding")}catch(v){x(v instanceof Error?v.message:"Registration failed.")}};return u.jsx("div",{className:"auth-page",children:u.jsxs("div",{className:"auth-shell",children:[u.jsx("main",{className:"auth-form-side",children:u.jsxs("div",{className:"auth-form-wrap auth-reveal",children:[u.jsxs("button",{type:"button",onClick:()=>s("/"),className:"auth-back",children:[u.jsx(Qf,{className:"h-4 w-4"})," Home"]}),u.jsx("div",{className:"mt-9",children:u.jsx("span",{className:"auth-brand",children:"pimp"})}),u.jsxs("div",{className:"mt-10",children:[u.jsx("h1",{className:"text-3xl font-semibold tracking-[-0.055em] text-slate-50",children:"Register Merchant"}),u.jsx("p",{className:"mt-3 text-sm text-slate-400",children:"Create a governed workspace for your store."})]}),u.jsxs("form",{onSubmit:w,className:"mt-7 space-y-4",children:[S&&u.jsxs("div",{className:"flex items-center gap-2 rounded-md border border-rose-400/25 bg-rose-400/10 p-3 text-xs font-medium text-rose-200",children:[u.jsx(gc,{className:"h-4 w-4 shrink-0"}),S]}),u.jsx(Lt,{className:"auth-input",label:"Store / Business Name",placeholder:"Apex Athletic",value:r,onChange:M,required:!0}),u.jsx(Lt,{className:"auth-input",label:"Store Slug",placeholder:"apex-athletic",value:l,onChange:A=>d(A.target.value.toLowerCase()),helperText:"Unique identifier for AI buyers",required:!0}),u.jsx(Lt,{className:"auth-input",label:"Admin Email",type:"email",placeholder:"admin@apex-athletic.com",value:f,onChange:A=>p(A.target.value),required:!0}),u.jsx(Lt,{className:"auth-input",label:"Razorpay Test Key ID",placeholder:"rzp_test_...",value:m,onChange:A=>_(A.target.value),helperText:"Test mode API key"}),u.jsxs(dt,{type:"submit",className:"mt-2 w-full rounded-md bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200",isLoading:t,children:["Create Store & Continue ",u.jsx(cr,{className:"h-4 w-4"})]})]}),u.jsxs("p",{className:"mt-7 text-center text-sm text-slate-400",children:["Already registered? ",u.jsx("button",{type:"button",onClick:()=>s("/login"),className:"font-medium text-slate-100 hover:underline",children:"Sign In"})]})]})}),u.jsxs("aside",{className:"auth-visual-side","aria-hidden":"true",children:[u.jsx("div",{className:"auth-dot-field"}),u.jsxs("div",{className:"auth-visual-copy",children:["Set your rules. ",u.jsx("span",{children:"Keep control."})]})]})]})})},fr=({className:s,children:e,...t})=>u.jsx("div",{className:En("rounded-lg border border-border bg-card text-card-foreground shadow-sm",s),...t,children:e}),qr=({className:s,children:e,...t})=>u.jsx("div",{className:En("flex flex-col space-y-1.5 p-6",s),...t,children:e}),ya=({className:s,children:e,...t})=>u.jsx("h3",{className:En("text-lg font-semibold leading-none tracking-tight",s),...t,children:e}),Sa=({className:s,children:e,...t})=>u.jsx("p",{className:En("text-sm text-muted-foreground",s),...t,children:e}),hr=({className:s,children:e,...t})=>u.jsx("div",{className:En("p-6 pt-0",s),...t,children:e}),e0=({className:s,children:e,...t})=>u.jsx("div",{className:En("flex items-center p-6 pt-0",s),...t,children:e}),_T=({steps:s,currentStep:e,className:t})=>u.jsx("div",{className:En("w-full",t),children:u.jsx("div",{className:"flex items-center justify-between",children:s.map((r,o)=>{const l=r.id<e,d=r.id===e;return u.jsxs(Nc.Fragment,{children:[u.jsxs("div",{className:"flex flex-col items-center",children:[u.jsx("div",{className:En("flex h-10 w-10 items-center justify-center rounded-full border-2 text-sm font-bold transition-all",l&&"border-primary bg-primary text-primary-foreground",d&&"border-primary bg-background text-primary ring-4 ring-primary/20",!l&&!d&&"border-border bg-muted text-muted-foreground"),children:l?u.jsx(Jf,{className:"h-5 w-5"}):r.id}),u.jsx("span",{className:En("mt-2 text-xs font-medium",d||l?"text-foreground":"text-muted-foreground"),children:r.title})]}),o<s.length-1&&u.jsx("div",{className:En("h-0.5 flex-1 mx-2 transition-colors",r.id<e?"bg-primary":"bg-border")})]},r.id)})})}),yT=({onNavigate:s})=>{const{merchant:e,updateProfile:t}=pr(),[r,o]=xe.useState(1),[l,d]=xe.useState(!1),[f,p]=xe.useState((e==null?void 0:e.name)||""),[m,_]=xe.useState((e==null?void 0:e.rzpKeyId)||"rzp_test_placeholder"),[S,x]=xe.useState((e==null?void 0:e.policies.autonomyLevel)??1),[M,w]=xe.useState((e==null?void 0:e.policies.maxDiscountPercentage)??15),[A,v]=xe.useState((e==null?void 0:e.policies.minMarginPercentage)??20),[y,P]=xe.useState(((e==null?void 0:e.policies.maxSingleTransactionPaise)??5e6)/100),U=[{id:1,title:"Identity"},{id:2,title:"Razorpay"},{id:3,title:"Policies"},{id:4,title:"Activate"}],N=()=>{r<4&&o(r+1)},L=()=>{r>1&&o(r-1)},R=async()=>{d(!0);try{const D=await Bt.completeSetup({name:f,rzpKeyId:m,autonomyLevel:S,maxDiscountPercentage:M,minMarginPercentage:A,maxSingleTransactionPaise:y*100});t(D),s("/dashboard")}finally{d(!1)}};return u.jsx("div",{className:"flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12",children:u.jsxs(fr,{className:"w-full max-w-xl border-border/80 bg-card/90 shadow-2xl",children:[u.jsxs(qr,{children:[u.jsx(_T,{steps:U,currentStep:r,className:"mb-6"}),u.jsxs(ya,{className:"text-xl",children:[r===1&&"Store Identity & Branding",r===2&&"Razorpay Settlement Gateway",r===3&&"Autonomous Policy Bounds",r===4&&"Review & Activate Control Plane"]}),u.jsxs(Sa,{children:[r===1&&"Confirm your store identity used by external buyer agents.",r===2&&"Configure testmode Razorpay credentials for payment capture.",r===3&&"Establish strict mathematical boundaries for AI negotiations.",r===4&&"Confirm your configuration and launch your agent-ready store."]})]}),u.jsxs(hr,{className:"space-y-4",children:[r===1&&u.jsxs("div",{className:"space-y-4",children:[u.jsx(Lt,{label:"Store Name",value:f,onChange:D=>p(D.target.value),placeholder:"e.g. Apex Athletic"}),u.jsx(Lt,{label:"Store Slug",value:(e==null?void 0:e.slug)||"",disabled:!0,helperText:"Store slug cannot be changed once created"}),u.jsx(Lt,{label:"Operating Currency",value:(e==null?void 0:e.currency)||"INR",disabled:!0})]}),r===2&&u.jsxs("div",{className:"space-y-4",children:[u.jsx(Lt,{label:"Razorpay API Key ID",value:m,onChange:D=>_(D.target.value),placeholder:"rzp_test_..."}),u.jsxs("div",{className:"rounded-md bg-secondary/60 p-3 text-xs text-muted-foreground space-y-1",children:[u.jsx("p",{className:"font-semibold text-foreground",children:"🔒 Zero Secret Leakage Invariant (INV-AGY-03)"}),u.jsx("p",{children:"Key secrets and database credentials are strictly held in the server environment and never exposed to the browser."})]})]}),r===3&&u.jsxs("div",{className:"space-y-4",children:[u.jsxs("div",{children:[u.jsx("label",{className:"block text-xs font-medium text-muted-foreground mb-1.5",children:"Autonomy Level"}),u.jsx("div",{className:"grid grid-cols-3 gap-2",children:[{level:0,name:"L0: Read-Only"},{level:1,name:"L1: Bounded"},{level:2,name:"L2: Supervised"}].map(D=>u.jsx("button",{type:"button",onClick:()=>x(D.level),className:`p-2.5 text-xs font-semibold rounded-md border text-center transition-colors ${S===D.level?"border-primary bg-primary/10 text-primary":"border-border bg-card text-muted-foreground hover:bg-accent"}`,children:D.name},D.level))})]}),u.jsxs("div",{className:"grid grid-cols-2 gap-3",children:[u.jsx(Lt,{label:"Max Discount (%)",type:"number",value:M,onChange:D=>w(parseFloat(D.target.value)||0),min:0,max:50,helperText:"Platform cap: 50%"}),u.jsx(Lt,{label:"Min Margin (%)",type:"number",value:A,onChange:D=>v(parseFloat(D.target.value)||0),min:0,max:100})]}),u.jsx(Lt,{label:"Max Single Transaction (₹)",type:"number",value:y,onChange:D=>P(parseFloat(D.target.value)||0),helperText:"Platform ceiling: ₹1,00,000"})]}),r===4&&u.jsxs("div",{className:"space-y-3 font-mono text-xs rounded-lg border border-border bg-muted/30 p-4",children:[u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Store Name:"}),u.jsx("span",{className:"font-semibold text-foreground",children:f})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Slug:"}),u.jsx("span",{className:"text-foreground",children:e==null?void 0:e.slug})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Autonomy Mode:"}),u.jsxs("span",{className:"text-primary font-bold",children:["Level ",S]})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Discount Ceiling:"}),u.jsxs("span",{className:"text-foreground",children:[M,"%"]})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Min Margin:"}),u.jsxs("span",{className:"text-foreground",children:[A,"%"]})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Max Tx Limit:"}),u.jsxs("span",{className:"text-foreground",children:["₹",y.toLocaleString("en-IN")]})]})]})]}),u.jsxs(e0,{className:"flex justify-between",children:[r>1?u.jsxs(dt,{onClick:L,variant:"outline",size:"sm",children:[u.jsx(Qf,{className:"h-4 w-4 mr-1"})," Back"]}):u.jsx("div",{}),r<4?u.jsxs(dt,{onClick:N,size:"sm",children:["Continue ",u.jsx(cr,{className:"h-4 w-4 ml-1"})]}):u.jsxs(dt,{onClick:R,isLoading:l,size:"sm",children:[u.jsx(Wr,{className:"h-4 w-4 mr-1"})," Complete & Launch"]})]})]})})},ST=({onNavigate:s})=>{const{merchant:e}=pr(),[t,r]=xe.useState(null),[o,l]=xe.useState(!0);xe.useEffect(()=>{(async()=>{try{const p=await Bt.getDashboardSummary();r(p)}catch{}finally{l(!1)}})()},[]);const d=(t==null?void 0:t.pending_approvals_count)??0;return u.jsxs("div",{className:"dashboard-page space-y-6",children:[d>0&&u.jsxs("div",{className:"flex items-center justify-between rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 shadow-glow-warning",children:[u.jsxs("div",{className:"flex items-center gap-3",children:[u.jsx("div",{className:"p-2 rounded-lg bg-amber-500/20 text-amber-400",children:u.jsx(ma,{className:"h-5 w-5"})}),u.jsxs("div",{children:[u.jsx("p",{className:"text-xs font-mono uppercase text-amber-400 font-bold tracking-wide",children:"Decision Required"}),u.jsxs("h3",{className:"text-sm font-semibold text-text-primary",children:[d," Escalated Buyer Proposal(s) Awaiting Review"]}),u.jsx("p",{className:"text-xs text-text-secondary",children:"Discounts exceeding autonomous policy thresholds have been halted and escalated for merchant authority."})]})]}),u.jsxs(dt,{onClick:()=>s("/approvals"),className:"bg-amber-500 hover:bg-amber-600 text-[#070B14] font-semibold text-xs shadow-sm",size:"sm",children:["Review Queue ",u.jsx(cr,{className:"h-3.5 w-3.5 ml-1"})]})]}),u.jsx("div",{className:"glass-panel rounded-2xl p-6 border border-[#24314A] bg-[#0D1424]/90 relative overflow-hidden",children:u.jsxs("div",{className:"flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10",children:[u.jsxs("div",{className:"space-y-1",children:[u.jsxs("div",{className:"inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-brand/10 border border-brand/25 text-brand-bright text-[11px] font-mono",children:[u.jsx(R_,{className:"h-3 w-3"}),"Store Autonomy Level ",(t==null?void 0:t.autonomy_level)??(e==null?void 0:e.policies.autonomyLevel)??1]}),u.jsx("h2",{className:"text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight",children:(e==null?void 0:e.name)||"Autonomous Store"}),u.jsx("p",{className:"text-xs text-text-secondary",children:"Server-authoritative commerce gateway actively securing buyer agent transactions on Razorpay."})]}),u.jsxs("div",{className:"flex flex-wrap items-center gap-3",children:[u.jsxs(dt,{onClick:()=>s("/demo"),className:"bg-brand hover:bg-brand-deep text-white text-xs font-semibold shadow-glow-sm",size:"sm",children:[u.jsx(rf,{className:"h-3.5 w-3.5 mr-1 text-brand-bright"}),"Launch Simulation Sandbox"]}),u.jsxs(dt,{onClick:()=>s("/policies"),variant:"outline",size:"sm",className:"text-xs bg-[#141D31] border-[#24314A] text-text-secondary hover:text-text-primary",children:[u.jsx(px,{className:"h-3.5 w-3.5 mr-1"}),"Policy Bounds"]})]})]})}),u.jsxs("div",{className:"grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",children:[u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted mb-2",children:[u.jsx("span",{children:"PENDING APPROVALS"}),u.jsx(Rc,{className:"h-4 w-4 text-amber-400"})]}),u.jsx("div",{className:"text-2xl sm:text-3xl font-bold text-amber-400",children:o?"...":d}),u.jsx("p",{className:"text-[11px] text-text-secondary mt-1",children:"Human-In-The-Loop tickets"})]}),u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted mb-2",children:[u.jsx("span",{children:"SETTLED REVENUE"}),u.jsx(Gy,{className:"h-4 w-4 text-emerald-400"})]}),u.jsx("div",{className:"text-2xl sm:text-3xl font-bold text-emerald-400",children:o?"...":fn((t==null?void 0:t.total_revenue_paise)??0)}),u.jsxs("p",{className:"text-[11px] text-text-secondary mt-1",children:[(t==null?void 0:t.total_orders)??0," settled order(s) via Razorpay"]})]}),u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted mb-2",children:[u.jsx("span",{children:"CATALOG PRODUCTS"}),u.jsx(vc,{className:"h-4 w-4 text-brand-bright"})]}),u.jsx("div",{className:"text-2xl sm:text-3xl font-bold text-text-primary",children:o?"...":(t==null?void 0:t.total_products)??0}),u.jsx("p",{className:"text-[11px] text-text-secondary mt-1",children:"Floor price protected items"})]}),u.jsxs("div",{className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover",children:[u.jsxs("div",{className:"flex items-center justify-between text-xs font-mono text-text-muted mb-2",children:[u.jsx("span",{children:"ACTIVE QUOTES"}),u.jsx(cx,{className:"h-4 w-4 text-blue-400"})]}),u.jsx("div",{className:"text-2xl sm:text-3xl font-bold text-text-primary",children:o?"...":(t==null?void 0:t.active_quotes_count)??0}),u.jsx("p",{className:"text-[11px] text-text-secondary mt-1",children:"In-flight buyer agent sessions"})]})]}),u.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-3 gap-4",children:[u.jsxs("div",{onClick:()=>s("/catalog"),className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover cursor-pointer",children:[u.jsxs("div",{className:"flex items-center gap-3 mb-2",children:[u.jsx("div",{className:"p-2 rounded-lg bg-brand/10 text-brand-bright",children:u.jsx(vc,{className:"h-4 w-4"})}),u.jsx("h4",{className:"text-xs font-bold text-text-primary",children:"Products & Floor Margins"})]}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"Manage product catalog, base pricing, and guaranteed floor price margins."})]}),u.jsxs("div",{onClick:()=>s("/inventory"),className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover cursor-pointer",children:[u.jsxs("div",{className:"flex items-center gap-3 mb-2",children:[u.jsx("div",{className:"p-2 rounded-lg bg-emerald-500/10 text-emerald-400",children:u.jsx(lx,{className:"h-4 w-4"})}),u.jsx("h4",{className:"text-xs font-bold text-text-primary",children:"Inventory & Row Locks"})]}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"Track stock levels and adjust reserves with PostgreSQL optimistic concurrency."})]}),u.jsxs("div",{onClick:()=>s("/audit"),className:"glass-card p-5 rounded-xl border border-[#24314A] card-hover cursor-pointer",children:[u.jsxs("div",{className:"flex items-center gap-3 mb-2",children:[u.jsx("div",{className:"p-2 rounded-lg bg-emerald-500/10 text-emerald-300",children:u.jsx(th,{className:"h-4 w-4"})}),u.jsx("h4",{className:"text-xs font-bold text-text-primary",children:"Cryptographic Audit Chain"})]}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed",children:"Inspect SHA-256 chained audit logs and verify real-time tamper resistance."})]})]}),u.jsxs("div",{className:"glass-panel p-5 rounded-xl border border-[#24314A] bg-[#0D1424]",children:[u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx(Pc,{className:"h-4 w-4 text-brand-bright"}),u.jsx("h4",{className:"text-xs font-bold text-text-primary uppercase tracking-wider font-mono",children:"Live Governance Policy Fingerprint"})]}),u.jsxs("span",{className:"text-[11px] font-mono text-emerald-400 flex items-center gap-1",children:[u.jsx(xc,{className:"h-3 w-3"}),"Server Authoritative"]})]}),u.jsx("div",{className:"font-mono text-xs bg-[#070B14] p-3 rounded-lg border border-[#24314A] text-brand-bright break-all",children:(t==null?void 0:t.policy_hash)||(e==null?void 0:e.policies.policyHash)||"0".repeat(64)}),u.jsx("p",{className:"text-[11px] text-text-muted mt-2",children:"This deterministic SHA-256 hash guarantees that merchant bounds (floor prices, max discounts, transaction caps) are cryptographically fixed onto every order and audit record."})]})]})},bn=({className:s,variant:e="default",children:t,...r})=>{const o={default:"bg-primary/20 text-primary border-primary/30",secondary:"bg-secondary text-secondary-foreground border-border",success:"bg-emerald-500/20 text-emerald-400 border-emerald-500/30",warning:"bg-amber-500/20 text-amber-400 border-amber-500/30",destructive:"bg-destructive/20 text-destructive border-destructive/30",outline:"border-border text-foreground"};return u.jsx("div",{className:En("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors uppercase tracking-wider",o[e],s),...r,children:t})},Po=({isOpen:s,onClose:e,title:t,description:r,children:o,className:l})=>(xe.useEffect(()=>{const d=f=>{f.key==="Escape"&&e()};return s&&(document.addEventListener("keydown",d),document.body.style.overflow="hidden"),()=>{document.removeEventListener("keydown",d),document.body.style.overflow="unset"}},[s,e]),s?u.jsxs("div",{className:"fixed inset-0 z-50 flex items-center justify-center p-4",children:[u.jsx("div",{className:"fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity",onClick:e}),u.jsxs("div",{role:"dialog","aria-modal":"true",className:En("relative z-50 w-full max-w-lg rounded-lg border border-border bg-card p-6 shadow-xl animate-in fade-in-0 zoom-in-95",l),children:[u.jsxs("button",{onClick:e,className:"absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring",children:[u.jsx(mx,{className:"h-4 w-4"}),u.jsx("span",{className:"sr-only",children:"Close"})]}),t&&u.jsx("h2",{className:"text-lg font-semibold tracking-tight",children:t}),r&&u.jsx("p",{className:"mt-1 text-sm text-muted-foreground",children:r}),u.jsx("div",{className:"mt-4",children:o})]})]}):null),MT=({children:s,className:e})=>u.jsx("div",{className:En("mt-6 flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 gap-2",e),children:s}),Yr=({icon:s,title:e,description:t,actionLabel:r,onAction:o,className:l})=>u.jsxs("div",{className:En("flex flex-col items-center justify-center rounded-lg border border-dashed border-border p-8 text-center",l),children:[s&&u.jsx("div",{className:"mb-4 text-muted-foreground",children:s}),u.jsx("h3",{className:"text-base font-semibold",children:e}),u.jsx("p",{className:"mt-1.5 max-w-sm text-sm text-muted-foreground",children:t}),r&&o&&u.jsx(dt,{onClick:o,className:"mt-6",size:"sm",children:r})]}),mr=({className:s,...e})=>u.jsx("div",{className:En("animate-pulse rounded-md bg-muted/60",s),...e}),bT=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState(!0),[o,l]=xe.useState(null),[d,f]=xe.useState(!1),[p,m]=xe.useState(!1),[_,S]=xe.useState(""),[x,M]=xe.useState(""),[w,A]=xe.useState("FOOTWEAR"),[v,y]=xe.useState(4999),[P,U]=xe.useState(3999),[N,L]=xe.useState(25),[R,D]=xe.useState(null),E=async()=>{r(!0),l(null);try{const z=await Bt.listProducts();e(z)}catch(z){l(z instanceof Error?z.message:"Failed to load catalog products.")}finally{r(!1)}};xe.useEffect(()=>{E()},[]);const I=async z=>{if(z.preventDefault(),P>v){D("Floor price cannot exceed base price.");return}D(null),m(!0);try{await Bt.createProduct({sku:_.trim(),title:x.trim(),category:w.trim(),base_price_paise:Math.round(v*100),floor_price_paise:Math.round(P*100),initial_stock:N}),f(!1),S(""),M(""),E()}catch(B){D(B instanceof Error?B.message:"Failed to create product.")}finally{m(!1)}};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-4",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Catalog & Products"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Authoritative catalog with deterministic floor prices and inventory binding."})]}),u.jsxs(dt,{onClick:()=>f(!0),size:"sm",className:"gap-1.5",children:[u.jsx(Ry,{className:"h-4 w-4"})," Add Product"]})]}),o&&u.jsxs("div",{className:"flex items-center gap-2 rounded-md bg-destructive/15 p-3 text-xs text-destructive font-medium",children:[u.jsx(gc,{className:"h-4 w-4 shrink-0"}),u.jsx("span",{children:o})]}),t?u.jsx("div",{className:"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",children:[1,2,3].map(z=>u.jsx(mr,{className:"h-44 w-full"},z))}):s.length===0?u.jsx(Yr,{icon:u.jsx(vc,{className:"h-10 w-10"}),title:"No products in catalog",description:"Create your first catalog item to enable AI buyer discovery and automated pricing.",actionLabel:"Add Product",onAction:()=>f(!0)}):u.jsx("div",{className:"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",children:s.map(z=>u.jsxs(fr,{className:"border-border bg-card/80",children:[u.jsxs(qr,{className:"pb-3",children:[u.jsxs("div",{className:"flex items-start justify-between gap-2",children:[u.jsxs("div",{children:[u.jsx(bn,{variant:"outline",className:"text-[10px] mb-1 font-mono",children:z.sku}),u.jsx(ya,{className:"text-base font-semibold",children:z.title})]}),u.jsx(bn,{variant:z.is_active?"success":"secondary",className:"text-[10px]",children:z.is_active?"ACTIVE":"INACTIVE"})]}),u.jsx(Sa,{className:"text-xs line-clamp-2",children:z.description||z.category})]}),u.jsxs(hr,{className:"space-y-2 text-xs border-t border-border pt-3",children:[u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Base Price:"}),u.jsx("span",{className:"font-semibold text-foreground",children:fn(z.base_price_paise)})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Floor Guard:"}),u.jsx("span",{className:"font-mono text-emerald-400 font-medium",children:fn(z.floor_price_paise)})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Available Stock:"}),u.jsxs("span",{className:`font-semibold ${z.available_stock<=2?"text-amber-400":"text-foreground"}`,children:[z.available_stock," units"]})]})]})]},z.id))}),u.jsx(Po,{isOpen:d,onClose:()=>f(!1),title:"Add New Catalog Product",description:"Configure product details, base price, and guaranteed floor price margin.",children:u.jsxs("form",{onSubmit:I,className:"space-y-3.5",children:[R&&u.jsxs("div",{className:"flex items-center gap-2 rounded-md bg-destructive/15 p-2.5 text-xs text-destructive font-medium",children:[u.jsx(gc,{className:"h-4 w-4 shrink-0"}),u.jsx("span",{children:R})]}),u.jsxs("div",{className:"grid grid-cols-2 gap-3",children:[u.jsx(Lt,{label:"SKU",placeholder:"RUN-AIR-01",value:_,onChange:z=>S(z.target.value),required:!0}),u.jsx(Lt,{label:"Category",placeholder:"FOOTWEAR",value:w,onChange:z=>A(z.target.value),required:!0})]}),u.jsx(Lt,{label:"Product Title",placeholder:"Air Velocity Running Shoes",value:x,onChange:z=>M(z.target.value),required:!0}),u.jsxs("div",{className:"grid grid-cols-2 gap-3",children:[u.jsx(Lt,{label:"Base Price (₹)",type:"number",value:v,onChange:z=>y(parseFloat(z.target.value)||0),min:1,required:!0}),u.jsx(Lt,{label:"Floor Price (₹)",type:"number",value:P,onChange:z=>U(parseFloat(z.target.value)||0),min:1,helperText:"Must be <= Base Price",required:!0})]}),u.jsx(Lt,{label:"Initial Stock Units",type:"number",value:N,onChange:z=>L(parseInt(z.target.value)||0),min:0,required:!0}),u.jsxs("div",{className:"flex justify-end gap-2 pt-3",children:[u.jsx(dt,{type:"button",onClick:()=>f(!1),variant:"outline",size:"sm",children:"Cancel"}),u.jsxs(dt,{type:"submit",isLoading:p,size:"sm",children:[u.jsx(Wr,{className:"h-4 w-4 mr-1"})," Save Product"]})]})]})})]})},ET=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState(!0),[o,l]=xe.useState(null),[d,f]=xe.useState(0),[p,m]=xe.useState("RESTOCK"),[_,S]=xe.useState(!1),[x,M]=xe.useState(null),w=async()=>{r(!0);try{const v=await Bt.listInventory();e(v)}catch{}finally{r(!1)}};xe.useEffect(()=>{w()},[]);const A=async v=>{if(v.preventDefault(),!!o){S(!0),M(null);try{await Bt.adjustInventory({sku:o.sku,quantity_delta:d,reason:p}),l(null),f(0),w()}catch(y){M(y instanceof Error?y.message:"Adjustment failed.")}finally{S(!1)}}};return u.jsxs("div",{className:"space-y-6",children:[u.jsx("div",{className:"flex items-center justify-between",children:u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Inventory Stocks"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Optimistic locking and atomic stock reservations for agent checkout."})]})}),t?u.jsx("div",{className:"space-y-3",children:[1,2,3].map(v=>u.jsx(mr,{className:"h-16 w-full"},v))}):s.length===0?u.jsx(Yr,{icon:u.jsx(lx,{className:"h-10 w-10"}),title:"No inventory records found",description:"Create catalog products to establish authoritative inventory stock tracking."}):u.jsx("div",{className:"rounded-lg border border-border bg-card overflow-hidden",children:u.jsxs("table",{className:"w-full text-xs text-left",children:[u.jsx("thead",{className:"bg-muted/40 text-muted-foreground uppercase text-[10px] border-b border-border",children:u.jsxs("tr",{children:[u.jsx("th",{className:"p-3.5",children:"SKU"}),u.jsx("th",{className:"p-3.5",children:"Product Title"}),u.jsx("th",{className:"p-3.5 text-right",children:"Available"}),u.jsx("th",{className:"p-3.5 text-right",children:"Reserved"}),u.jsx("th",{className:"p-3.5 text-right",children:"Safety Threshold"}),u.jsx("th",{className:"p-3.5 text-center",children:"Status"}),u.jsx("th",{className:"p-3.5 text-right",children:"Actions"})]})}),u.jsx("tbody",{className:"divide-y border-border font-medium",children:s.map(v=>{const y=v.available_quantity<=v.safety_threshold;return u.jsxs("tr",{className:"hover:bg-accent/30 transition-colors",children:[u.jsx("td",{className:"p-3.5 font-mono text-primary",children:v.sku}),u.jsx("td",{className:"p-3.5 font-semibold text-foreground",children:v.product_title}),u.jsx("td",{className:"p-3.5 text-right font-bold text-foreground",children:v.available_quantity}),u.jsx("td",{className:"p-3.5 text-right text-muted-foreground",children:v.reserved_quantity}),u.jsx("td",{className:"p-3.5 text-right text-muted-foreground",children:v.safety_threshold}),u.jsx("td",{className:"p-3.5 text-center",children:u.jsx(bn,{variant:y?"warning":"success",className:"text-[9px]",children:y?"LOW STOCK":"IN STOCK"})}),u.jsx("td",{className:"p-3.5 text-right",children:u.jsxs(dt,{onClick:()=>{l(v),f(0)},variant:"outline",size:"sm",className:"h-7 text-xs gap-1",children:[u.jsx(Ty,{className:"h-3 w-3"})," Adjust"]})})]},v.id)})})]})}),u.jsx(Po,{isOpen:!!o,onClose:()=>l(null),title:`Adjust Stock for ${o==null?void 0:o.sku}`,description:"Add or remove available stock units with server-authoritative optimistic locking.",children:u.jsxs("form",{onSubmit:A,className:"space-y-4",children:[x&&u.jsxs("div",{className:"flex items-center gap-2 rounded bg-destructive/15 p-2.5 text-xs text-destructive",children:[u.jsx(ma,{className:"h-4 w-4 shrink-0"}),u.jsx("span",{children:x})]}),u.jsxs("div",{className:"rounded bg-muted/40 p-3 text-xs space-y-1",children:[u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Current Available:"}),u.jsxs("span",{className:"font-bold text-foreground",children:[o==null?void 0:o.available_quantity," units"]})]}),u.jsxs("div",{className:"flex justify-between",children:[u.jsx("span",{className:"text-muted-foreground",children:"Projected New Stock:"}),u.jsxs("span",{className:"font-bold text-primary",children:[((o==null?void 0:o.available_quantity)||0)+d," units"]})]})]}),u.jsx(Lt,{label:"Quantity Delta (+ to add, - to subtract)",type:"number",value:d,onChange:v=>f(parseInt(v.target.value)||0),required:!0}),u.jsx(Lt,{label:"Reason",value:p,onChange:v=>m(v.target.value),placeholder:"RESTOCK / CORRECTION",required:!0}),u.jsxs("div",{className:"flex justify-end gap-2 pt-2",children:[u.jsx(dt,{type:"button",onClick:()=>l(null),variant:"outline",size:"sm",children:"Cancel"}),u.jsxs(dt,{type:"submit",isLoading:_,size:"sm",children:[u.jsx(Wr,{className:"h-4 w-4 mr-1"})," Commit Adjustment"]})]})]})})]})},wT=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState(!0);xe.useEffect(()=>{(async()=>{try{const d=await Bt.listQuotes();e(d)}finally{r(!1)}})()},[]);const o=l=>{switch(l){case"ACCEPTED":return u.jsx(bn,{variant:"success",children:"ACCEPTED"});case"PROPOSED":return u.jsx(bn,{variant:"default",children:"PROPOSED"});case"NEGOTIATING":return u.jsx(bn,{variant:"warning",children:"NEGOTIATING"});case"REJECTED":return u.jsx(bn,{variant:"destructive",children:"REJECTED"});default:return u.jsx(bn,{variant:"secondary",children:l})}};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Price Quotes & Binding Offers"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Binding commercial proposals issued by the Deterministic Policy Engine."})]}),t?u.jsx("div",{className:"space-y-3",children:[1,2,3].map(l=>u.jsx(mr,{className:"h-20 w-full"},l))}):s.length===0?u.jsx(Yr,{icon:u.jsx(ry,{className:"h-10 w-10"}),title:"No quotes recorded",description:"Price quotes generated by AI buyers or agent negotiation sessions will appear here."}):u.jsx("div",{className:"space-y-4",children:s.map(l=>u.jsxs(fr,{className:"border-border bg-card/80",children:[u.jsx(qr,{className:"pb-3",children:u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-2",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsxs("span",{className:"font-mono text-xs text-muted-foreground",children:[l.id.slice(0,8),"..."]}),o(l.status)]}),u.jsxs("div",{className:"flex items-center gap-3 text-xs text-muted-foreground",children:[u.jsxs("span",{className:"flex items-center gap-1",children:[u.jsx(Rc,{className:"h-3.5 w-3.5"}),"Created ",ba(l.created_at)]}),u.jsx("span",{className:"font-bold text-foreground text-sm",children:fn(l.total_paise)})]})]})}),u.jsxs(hr,{className:"border-t border-border pt-3 text-xs space-y-2",children:[u.jsxs("div",{className:"flex justify-between text-muted-foreground",children:[u.jsxs("span",{children:["Subtotal: ",fn(l.subtotal_paise)]}),u.jsxs("span",{children:["Discount: ",fn(l.discount_paise)]}),u.jsxs("span",{children:["Shipping: ",fn(l.shipping_paise)]})]}),l.discount_reason&&u.jsxs("p",{className:"text-[11px] text-primary italic",children:["Reason: ",l.discount_reason]}),u.jsx("div",{className:"mt-2 space-y-1 bg-muted/20 p-2 rounded",children:l.items.map((d,f)=>u.jsxs("div",{className:"flex justify-between text-[11px]",children:[u.jsxs("span",{children:[d.quantity,"x ",d.title," (",d.sku,")"]}),u.jsx("span",{className:"font-mono",children:fn(d.total_price_paise)})]},f))})]})]},l.id))})]})},TT=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState(!0),[o,l]=xe.useState(null),[d,f]=xe.useState(null),p=async()=>{r(!0);try{const _=await Bt.listOrders();e(_)}finally{r(!1)}};xe.useEffect(()=>{p()},[]);const m=async _=>{l(_);try{const S=await Bt.reconcileOrder(_);f(`Reconciliation complete for order ${_.slice(0,8)} (Status: ${S.status||"PROCESSED"})`),p()}catch(S){f(`Reconciliation error: ${S instanceof Error?S.message:"Failed"}`)}finally{l(null)}};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Orders & Settlement"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Server-authoritative merchant order ledger backed by Razorpay payments."})]}),d&&u.jsxs("div",{className:"flex items-center justify-between rounded bg-primary/10 border border-primary/30 p-3 text-xs text-primary",children:[u.jsx("span",{children:d}),u.jsx("button",{onClick:()=>f(null),className:"font-bold",children:"✕"})]}),t?u.jsx("div",{className:"space-y-3",children:[1,2,3].map(_=>u.jsx(mr,{className:"h-20 w-full"},_))}):s.length===0?u.jsx(Yr,{icon:u.jsx(hx,{className:"h-10 w-10"}),title:"No orders committed",description:"Orders placed by external AI buyers through Razorpay checkout will be listed here."}):u.jsx("div",{className:"rounded-lg border border-border bg-card overflow-hidden",children:u.jsxs("table",{className:"w-full text-xs text-left",children:[u.jsx("thead",{className:"bg-muted/40 text-muted-foreground uppercase text-[10px] border-b border-border",children:u.jsxs("tr",{children:[u.jsx("th",{className:"p-3.5",children:"Order ID"}),u.jsx("th",{className:"p-3.5",children:"Buyer Email"}),u.jsx("th",{className:"p-3.5",children:"Razorpay Order"}),u.jsx("th",{className:"p-3.5 text-right",children:"Amount"}),u.jsx("th",{className:"p-3.5 text-center",children:"Status"}),u.jsx("th",{className:"p-3.5",children:"Date"}),u.jsx("th",{className:"p-3.5 text-right",children:"Actions"})]})}),u.jsx("tbody",{className:"divide-y border-border font-medium",children:s.map(_=>u.jsxs("tr",{className:"hover:bg-accent/30 transition-colors",children:[u.jsxs("td",{className:"p-3.5 font-mono text-primary",children:[_.id.slice(0,8),"..."]}),u.jsx("td",{className:"p-3.5 text-foreground",children:_.buyer_email}),u.jsx("td",{className:"p-3.5 font-mono text-muted-foreground",children:_.rzp_order_id||"PENDING"}),u.jsx("td",{className:"p-3.5 text-right font-bold text-foreground",children:fn(_.amount_paise)}),u.jsx("td",{className:"p-3.5 text-center",children:u.jsx(bn,{variant:_.status==="PAID"?"success":_.status==="CREATED"?"default":"secondary",className:"text-[9px]",children:_.status})}),u.jsx("td",{className:"p-3.5 text-muted-foreground",children:ba(_.created_at)}),u.jsx("td",{className:"p-3.5 text-right",children:u.jsxs(dt,{onClick:()=>m(_.id),isLoading:o===_.id,variant:"outline",size:"sm",className:"h-7 text-xs gap-1",children:[u.jsx(Ly,{className:"h-3 w-3"})," Reconcile"]})})]},_.id))})]})})]})},AT=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState(!0);return xe.useEffect(()=>{(async()=>{try{const l=await Bt.listPayments();e(l)}finally{r(!1)}})()},[]),u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Payment Attempts & Settlements"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Razorpay capture attempts, webhook verification results, and transaction binding references."})]}),t?u.jsx("div",{className:"space-y-3",children:[1,2,3].map(o=>u.jsx(mr,{className:"h-16 w-full"},o))}):s.length===0?u.jsx(Yr,{icon:u.jsx(eh,{className:"h-10 w-10"}),title:"No payment attempts logged",description:"When payment capture occurs via webhook or settlement fetch, records will appear here."}):u.jsx("div",{className:"rounded-lg border border-border bg-card overflow-hidden",children:u.jsxs("table",{className:"w-full text-xs text-left",children:[u.jsx("thead",{className:"bg-muted/40 text-muted-foreground uppercase text-[10px] border-b border-border",children:u.jsxs("tr",{children:[u.jsx("th",{className:"p-3.5",children:"Payment ID"}),u.jsx("th",{className:"p-3.5",children:"Razorpay Payment"}),u.jsx("th",{className:"p-3.5",children:"Razorpay Order"}),u.jsx("th",{className:"p-3.5 text-right",children:"Amount"}),u.jsx("th",{className:"p-3.5 text-center",children:"Status"}),u.jsx("th",{className:"p-3.5",children:"Method"}),u.jsx("th",{className:"p-3.5",children:"Date"})]})}),u.jsx("tbody",{className:"divide-y divide-border font-medium",children:s.map(o=>u.jsxs("tr",{className:"hover:bg-accent/30 transition-colors",children:[u.jsxs("td",{className:"p-3.5 font-mono text-primary",children:[o.id.slice(0,8),"..."]}),u.jsx("td",{className:"p-3.5 font-mono text-muted-foreground",children:o.rzp_payment_id||"N/A"}),u.jsx("td",{className:"p-3.5 font-mono text-muted-foreground",children:o.rzp_order_id}),u.jsx("td",{className:"p-3.5 text-right font-bold text-foreground",children:fn(o.amount_paise)}),u.jsx("td",{className:"p-3.5 text-center",children:u.jsx(bn,{variant:o.status==="CAPTURED"?"success":o.status==="FAILED"?"destructive":"default",className:"text-[9px]",children:o.status})}),u.jsx("td",{className:"p-3.5 uppercase",children:o.payment_method||"CARD / UPI"}),u.jsx("td",{className:"p-3.5 text-muted-foreground",children:ba(o.created_at)})]},o.id))})]})})]})},CT=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState(!0);return xe.useEffect(()=>{(async()=>{try{const l=await Bt.listQuotes();e(l.filter(d=>d.discount_paise>0||d.status==="NEGOTIATING"))}finally{r(!1)}})()},[]),u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Negotiations Trace"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Multi-round buyer agent price negotiations bounded by the 3-round limit and floor price."})]}),t?u.jsx("div",{className:"space-y-3",children:[1,2].map(o=>u.jsx(mr,{className:"h-28 w-full"},o))}):s.length===0?u.jsx(Yr,{icon:u.jsx(_y,{className:"h-10 w-10"}),title:"No active negotiations",description:"Negotiations initiated by external AI buyers will appear here with requested terms."}):u.jsx("div",{className:"space-y-4",children:s.map(o=>u.jsxs(fr,{className:"border-border bg-card/80",children:[u.jsx(qr,{className:"pb-3",children:u.jsxs("div",{className:"flex items-center justify-between",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsxs("span",{className:"font-mono text-xs text-primary font-semibold",children:[o.id.slice(0,8),"..."]}),u.jsx(bn,{variant:o.status==="ACCEPTED"?"success":"warning",className:"text-[9px]",children:o.status})]}),u.jsx("span",{className:"text-xs text-muted-foreground",children:ba(o.created_at)})]})}),u.jsxs(hr,{className:"border-t border-border pt-3 text-xs space-y-2",children:[u.jsxs("div",{className:"flex items-center justify-between bg-muted/20 p-3 rounded",children:[u.jsxs("div",{children:[u.jsx("span",{className:"text-muted-foreground",children:"Catalog Subtotal:"}),u.jsx("p",{className:"font-bold text-foreground",children:fn(o.subtotal_paise)})]}),u.jsx(cr,{className:"h-4 w-4 text-muted-foreground"}),u.jsxs("div",{children:[u.jsx("span",{className:"text-muted-foreground",children:"Granted Discount:"}),u.jsxs("p",{className:"font-bold text-amber-400",children:["-",fn(o.discount_paise)]})]}),u.jsx(cr,{className:"h-4 w-4 text-muted-foreground"}),u.jsxs("div",{children:[u.jsx("span",{className:"text-muted-foreground",children:"Final Settlement:"}),u.jsx("p",{className:"font-bold text-emerald-400",children:fn(o.total_paise)})]})]}),o.discount_reason&&u.jsxs("p",{className:"text-[11px] text-muted-foreground italic",children:["Policy Verdict: ",o.discount_reason]})]})]},o.id))})]})},NT=()=>{const[s,e]=xe.useState([]),[t,r]=xe.useState("PENDING"),[o,l]=xe.useState(!0),[d,f]=xe.useState(null),[p,m]=xe.useState("APPROVE"),[_,S]=xe.useState(""),[x,M]=xe.useState(!1),[w,A]=xe.useState(null),v=async()=>{l(!0);try{const P=await Bt.listApprovals(t);e(P)}finally{l(!1)}};xe.useEffect(()=>{v()},[t]);const y=async P=>{if(P.preventDefault(),!!d){M(!0),A(null);try{await Bt.resolveApproval(d.id,{decision:p,reason_note:_.trim()||`Merchant ${p}`}),f(null),S(""),v()}catch(U){A(U instanceof Error?U.message:"Resolution failed.")}finally{M(!1)}}};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-4",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight text-text-primary",children:"Human Approval Decision Workbench (HITL)"}),u.jsx("p",{className:"text-xs text-text-secondary mt-0.5",children:"Server-escalated buyer agent discount proposals requiring authoritative merchant clearance."})]}),u.jsx("div",{className:"flex gap-1 bg-[#0D1424] p-1 rounded-xl border border-[#24314A]",children:["PENDING","APPROVED","REJECTED","ALL"].map(P=>u.jsx("button",{onClick:()=>r(P),className:`px-3 py-1.5 text-xs font-mono font-medium rounded-lg transition-all ${t===P?"bg-brand text-white shadow-sm font-semibold":"text-text-muted hover:text-text-primary hover:bg-[#141D31]"}`,children:P},P))})]}),o?u.jsx("div",{className:"space-y-3",children:[1,2,3].map(P=>u.jsx(mr,{className:"h-32 w-full rounded-xl bg-[#0D1424]"},P))}):s.length===0?u.jsx("div",{className:"glass-panel rounded-2xl p-10 text-center border border-[#24314A]",children:u.jsx(Yr,{icon:u.jsx(Rc,{className:"h-10 w-10 text-brand-bright"}),title:`No ${t.toLowerCase()} approval tickets`,description:"When buyer negotiations exceed autonomous policy limits, tickets are escalated here for merchant review."})}):u.jsx("div",{className:"space-y-4",children:s.map(P=>{const U=P.status==="PENDING";return u.jsxs("div",{className:`glass-panel rounded-xl p-5 border transition-all ${U?"border-amber-500/40 bg-[#0D1424]/90 shadow-glow-warning":"border-[#24314A] bg-[#0D1424]/60 opacity-90"}`,children:[u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4",children:[u.jsxs("div",{className:"flex items-center gap-3",children:[u.jsxs("span",{className:"font-mono text-xs text-brand-bright font-bold",children:["Ticket ",P.id.slice(0,8)]}),u.jsx(bn,{variant:P.status==="PENDING"?"warning":P.status==="APPROVED"?"success":"destructive",className:"text-[10px] font-mono",children:P.status})]}),u.jsx("span",{className:"text-[11px] font-mono text-text-muted",children:ba(P.created_at)})]}),u.jsxs("div",{className:"grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#070B14] p-3.5 rounded-xl border border-[#24314A]/80 mb-3",children:[u.jsxs("div",{children:[u.jsx("span",{className:"text-[10px] font-mono text-text-muted uppercase",children:"Requested Offer"}),u.jsx("p",{className:"font-bold text-text-primary text-sm mt-0.5",children:fn(P.requested_amount_paise)})]}),u.jsxs("div",{children:[u.jsx("span",{className:"text-[10px] font-mono text-text-muted uppercase",children:"Proposed Discount"}),u.jsxs("p",{className:"font-bold text-amber-400 text-sm mt-0.5",children:["-",fn(P.proposed_discount_paise)]})]}),u.jsxs("div",{children:[u.jsx("span",{className:"text-[10px] font-mono text-text-muted uppercase",children:"Discount Rate"}),u.jsxs("p",{className:"font-bold text-text-primary text-sm mt-0.5",children:[P.proposed_discount_percentage,"%"]})]}),u.jsxs("div",{children:[u.jsx("span",{className:"text-[10px] font-mono text-text-muted uppercase",children:"Policy Code"}),u.jsx("p",{className:"font-mono text-xs text-brand-bright mt-0.5 truncate",children:P.policy_rule_code})]})]}),P.reason_note&&u.jsxs("div",{className:"text-xs text-text-secondary italic mb-3 bg-[#141D31]/40 px-3 py-1.5 rounded-lg border border-[#24314A]/40",children:["Resolution note: ",P.reason_note]}),U&&u.jsxs("div",{className:"flex justify-end gap-2.5 pt-2 border-t border-[#24314A]/60",children:[u.jsxs(dt,{onClick:()=>{f(P),m("REJECT"),S("")},variant:"outline",size:"sm",className:"text-xs text-rose-400 border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-300",children:[u.jsx(j_,{className:"h-3.5 w-3.5 mr-1"})," Reject Offer"]}),u.jsxs(dt,{onClick:()=>{f(P),m("APPROVE"),S("")},size:"sm",className:"text-xs bg-emerald-500 hover:bg-emerald-600 text-[#070B14] font-semibold shadow-glow-success",children:[u.jsx(Wr,{className:"h-3.5 w-3.5 mr-1"})," Approve Offer"]})]})]},P.id)})}),u.jsx(Po,{isOpen:!!d,onClose:()=>f(null),title:`${p==="APPROVE"?"Approve":"Reject"} Ticket ${d==null?void 0:d.id.slice(0,8)}`,description:`Authoritatively ${p.toLowerCase()} the requested counter-offer of ${fn((d==null?void 0:d.requested_amount_paise)||0)}.`,children:u.jsxs("form",{onSubmit:y,className:"space-y-4",children:[w&&u.jsxs("div",{className:"flex items-center gap-2 rounded-lg bg-rose-500/15 border border-rose-500/30 p-2.5 text-xs text-rose-300",children:[u.jsx(ma,{className:"h-4 w-4 shrink-0"}),u.jsx("span",{children:w})]}),u.jsx(Lt,{label:"Authoritative Reason Note",placeholder:"e.g. Approved bulk order discount / Below floor margin rejection",value:_,onChange:P=>S(P.target.value),required:!0}),u.jsxs("div",{className:"flex justify-end gap-2.5 pt-2",children:[u.jsx(dt,{type:"button",onClick:()=>f(null),variant:"outline",size:"sm",className:"text-xs",children:"Cancel"}),u.jsxs(dt,{type:"submit",isLoading:x,className:`text-xs ${p==="APPROVE"?"bg-emerald-500 hover:bg-emerald-600 text-[#070B14] font-bold":"bg-rose-500 hover:bg-rose-600 text-white"}`,size:"sm",children:["Confirm ",p]})]})]})})]})},RT=()=>{const{updateProfile:s}=pr(),[e,t]=xe.useState(null),[r,o]=xe.useState(!0),[l,d]=xe.useState(!1),[f,p]=xe.useState(null),[m,_]=xe.useState(null),[S,x]=xe.useState(1),[M,w]=xe.useState(15),[A,v]=xe.useState(20),[y,P]=xe.useState(5e4),U=async()=>{o(!0);try{const L=await Bt.getPolicies();t(L),x(L.autonomy_level),w(L.max_discount_percentage),v(L.min_margin_percentage),P(L.max_single_transaction_paise/100)}finally{o(!1)}};xe.useEffect(()=>{U()},[]);const N=async L=>{L.preventDefault(),d(!0),_(null),p(null);try{const R=await Bt.updatePolicies({autonomy_level:S,max_discount_percentage:M,min_margin_percentage:A,max_single_transaction_paise:Math.round(y*100)});t(R),s({policies:{autonomyLevel:R.autonomy_level,maxDiscountPercentage:R.max_discount_percentage,minMarginPercentage:R.min_margin_percentage,maxSingleTransactionPaise:R.max_single_transaction_paise,policyHash:R.policy_hash,protocolVersion:R.protocol_version}}),p("Policy rules and deterministic SHA-256 hash updated successfully.")}catch(R){_(R instanceof Error?R.message:"Failed to update policy rules.")}finally{d(!1)}};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Policy Rules & Autonomy Governance"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Deterministic mathematical safety boundaries enforced on all AI agent interactions."})]}),f&&u.jsxs("div",{className:"flex items-center gap-2 rounded bg-emerald-500/15 border border-emerald-500/30 p-3 text-xs text-emerald-400 font-medium",children:[u.jsx(Wr,{className:"h-4 w-4 shrink-0"}),u.jsx("span",{children:f})]}),m&&u.jsxs("div",{className:"flex items-center gap-2 rounded bg-destructive/15 p-3 text-xs text-destructive font-medium",children:[u.jsx(ma,{className:"h-4 w-4 shrink-0"}),u.jsx("span",{children:m})]}),r?u.jsx(mr,{className:"h-96 w-full"}):u.jsxs("form",{onSubmit:N,className:"grid grid-cols-1 lg:grid-cols-3 gap-6",children:[u.jsxs(fr,{className:"lg:col-span-2 border-border bg-card/90",children:[u.jsxs(qr,{children:[u.jsx(ya,{className:"text-base",children:"Merchant Autonomy & Financial Bounds"}),u.jsx(Sa,{children:"Adjust discount ceilings, minimum profit margins, and single transaction caps."})]}),u.jsxs(hr,{className:"space-y-4",children:[u.jsxs("div",{children:[u.jsx("label",{className:"block text-xs font-medium text-muted-foreground mb-1.5",children:"Autonomy Level"}),u.jsx("div",{className:"grid grid-cols-3 gap-2",children:[{level:0,label:"Level 0",desc:"Read-Only (No Negotiation)"},{level:1,label:"Level 1",desc:"Bounded Auto-Acceptance"},{level:2,label:"Level 2",desc:"Supervised HITL Escalation"}].map(L=>u.jsxs("button",{type:"button",onClick:()=>x(L.level),className:`p-3 text-left rounded-md border transition-all ${S===L.level?"border-primary bg-primary/10 text-primary ring-1 ring-primary":"border-border bg-card text-muted-foreground hover:bg-accent"}`,children:[u.jsx("p",{className:"font-bold text-xs",children:L.label}),u.jsx("p",{className:"text-[10px] text-muted-foreground mt-0.5",children:L.desc})]},L.level))})]}),u.jsxs("div",{className:"grid grid-cols-1 sm:grid-cols-2 gap-3",children:[u.jsx(Lt,{label:"Max Discount Percentage (%)",type:"number",value:M,onChange:L=>w(parseFloat(L.target.value)||0),min:0,max:50,helperText:"Platform ceiling: 50%",required:!0}),u.jsx(Lt,{label:"Minimum Margin Percentage (%)",type:"number",value:A,onChange:L=>v(parseFloat(L.target.value)||0),min:0,max:100,required:!0})]}),u.jsx(Lt,{label:"Max Single Transaction Limit (₹)",type:"number",value:y,onChange:L=>P(parseFloat(L.target.value)||0),min:1,max:1e5,helperText:"Platform transaction ceiling: ₹1,00,000",required:!0})]}),u.jsx(e0,{className:"flex justify-end border-t border-border pt-4",children:u.jsxs(dt,{type:"submit",isLoading:l,size:"sm",children:[u.jsx(Wr,{className:"h-4 w-4 mr-1"})," Save Policy Rules"]})})]}),u.jsx("div",{className:"space-y-4",children:u.jsxs(fr,{className:"border-border bg-card/90",children:[u.jsxs(qr,{children:[u.jsxs("div",{className:"flex items-center gap-2 text-primary",children:[u.jsx(Pc,{className:"h-5 w-5"}),u.jsx(ya,{className:"text-base",children:"Policy Hash"})]}),u.jsx(Sa,{children:"SHA-256 fingerprint generated over normalized governance rules."})]}),u.jsxs(hr,{className:"space-y-3",children:[u.jsx("div",{className:"font-mono text-xs bg-muted/40 p-3 rounded border border-border text-foreground break-all",children:e==null?void 0:e.policy_hash}),u.jsx("p",{className:"text-[11px] text-muted-foreground",children:"Stamping this hash onto all transactions guarantees cryptographic non-repudiation of policy state."})]})]})})]})]})},PT=()=>{const[s,e]=xe.useState(null),[t,r]=xe.useState(!0);return xe.useEffect(()=>{(async()=>{try{const l=await Bt.getAuditLedger(50);e(l)}finally{r(!1)}})()},[]),u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-4",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Audit Trail & Cryptographic Ledger"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Immutable, SHA-256 hash-chained record of all domain mutations and financial events."})]}),s&&u.jsx("div",{className:"flex items-center gap-2",children:s.chain_valid?u.jsxs(bn,{variant:"success",className:"gap-1 px-3 py-1",children:[u.jsx(Pc,{className:"h-3.5 w-3.5"})," Chain Verified: 100% Intact"]}):u.jsxs(bn,{variant:"destructive",className:"gap-1 px-3 py-1",children:[u.jsx(fx,{className:"h-3.5 w-3.5"})," Hash Mismatch Detected"]})})]}),t?u.jsx("div",{className:"space-y-3",children:[1,2,3].map(o=>u.jsx(mr,{className:"h-20 w-full"},o))}):!s||s.events.length===0?u.jsx(Yr,{icon:u.jsx(th,{className:"h-10 w-10"}),title:"No audit events logged",description:"System mutations and financial events will append to this immutable ledger."}):u.jsx("div",{className:"space-y-3",children:s.events.map(o=>u.jsx(fr,{className:"border-border bg-card/80",children:u.jsxs(hr,{className:"p-4 space-y-2",children:[u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx(bn,{variant:"default",className:"text-[10px] font-mono",children:o.event_type}),u.jsx("span",{className:"font-semibold text-foreground",children:o.actor_type})]}),u.jsxs("div",{className:"flex items-center gap-3 text-muted-foreground font-mono text-[11px]",children:[u.jsxs("span",{children:["Hash: ",o.event_hash.slice(0,12),"..."]}),u.jsx("span",{children:ba(o.created_at)})]})]}),u.jsx("div",{className:"bg-background/80 p-2.5 rounded border border-border font-mono text-[11px] text-muted-foreground overflow-x-auto",children:u.jsx("pre",{children:JSON.stringify(o.payload,null,2)})})]})},o.id))})]})},LT=()=>{const{merchant:s}=pr(),[e,t]=xe.useState(null),r=(o,l)=>{navigator.clipboard.writeText(o),t(l),setTimeout(()=>t(null),2e3)};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight",children:"Merchant Settings"}),u.jsx("p",{className:"text-xs text-muted-foreground mt-0.5",children:"Store identity, Razorpay integration keys, and public ACP agent endpoint URLs."})]}),u.jsxs("div",{className:"grid grid-cols-1 lg:grid-cols-2 gap-6",children:[u.jsxs(fr,{className:"border-border bg-card/90",children:[u.jsxs(qr,{children:[u.jsx(ya,{className:"text-base",children:"Store Identity"}),u.jsx(Sa,{children:"Authoritative merchant profile configured in ARM."})]}),u.jsxs(hr,{className:"space-y-3 text-xs",children:[u.jsx(Lt,{label:"Store Name",value:(s==null?void 0:s.name)||"",disabled:!0}),u.jsx(Lt,{label:"Store Slug",value:(s==null?void 0:s.slug)||"",disabled:!0}),u.jsx(Lt,{label:"Operating Currency",value:(s==null?void 0:s.currency)||"INR",disabled:!0}),u.jsx(Lt,{label:"Merchant UUID",value:(s==null?void 0:s.merchantId)||"",disabled:!0})]})]}),u.jsxs(fr,{className:"border-border bg-card/90",children:[u.jsxs(qr,{children:[u.jsx(ya,{className:"text-base",children:"Agent Commerce Protocol (ACP) Endpoints"}),u.jsx(Sa,{children:"Public endpoints exposed to external AI buyer agents."})]}),u.jsxs(hr,{className:"space-y-4 text-xs",children:[u.jsxs("div",{children:[u.jsx("label",{className:"block text-xs font-medium text-muted-foreground mb-1",children:"ACP Wire Endpoint"}),u.jsxs("div",{className:"flex gap-2",children:[u.jsx("input",{readOnly:!0,value:"https://api.agentready.merchant/api/v1/protocol/acp",className:"flex h-9 w-full rounded border border-input bg-muted/40 px-3 font-mono text-xs text-muted-foreground"}),u.jsx(dt,{onClick:()=>r("https://api.agentready.merchant/api/v1/protocol/acp","acp"),variant:"outline",size:"sm",children:e==="acp"?u.jsx(Jf,{className:"h-4 w-4 text-emerald-400"}):u.jsx(X_,{className:"h-4 w-4"})})]})]}),u.jsxs("div",{children:[u.jsx("label",{className:"block text-xs font-medium text-muted-foreground mb-1",children:"Razorpay Key Identifier"}),u.jsx("input",{readOnly:!0,value:(s==null?void 0:s.rzpKeyId)||"rzp_test_placeholder",className:"flex h-9 w-full rounded border border-input bg-muted/40 px-3 font-mono text-xs text-muted-foreground"})]})]})]})]})]})},IT=()=>{const[s,e]=xe.useState("STANDARD_AUTO_COMMERCE"),[t,r]=xe.useState("RUN-PRO-01"),[o,l]=xe.useState(1),[d,f]=xe.useState("10"),[p,m]=xe.useState(!1),[_,S]=xe.useState(null),[x,M]=xe.useState(null),[w,A]=xe.useState(!1),[v,y]=xe.useState(!1),[P,U]=xe.useState(null),N=async()=>{m(!0),M(null),S(null);const R={scenario:s,sku:t,quantity:o,target_discount_pct:s==="HITL_ESCALATION_COMMERCE"?20:parseFloat(d)||10};try{const D=await Bt.simulateDemo(R);S(D)}catch(D){M(D instanceof Error?D.message:"Simulation failed")}finally{m(!1)}},L=async()=>{y(!0),M(null),U(null);try{const R=await Bt.seedDemoState();U(R.message),A(!1)}catch(R){M(R instanceof Error?R.message:"Failed to reset demo state")}finally{y(!1)}};return u.jsxs("div",{className:"space-y-6",children:[u.jsxs("div",{className:"flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#24314A]/70 pb-4",children:[u.jsxs("div",{children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx("h2",{className:"text-xl font-bold tracking-tight text-text-primary",children:"Interactive Simulation Sandbox"}),u.jsx("span",{className:"px-2 py-0.5 rounded text-[10px] font-mono bg-brand/20 text-brand-bright border border-brand/30",children:"Deterministic Sandbox"})]}),u.jsx("p",{className:"text-xs text-text-secondary mt-0.5",children:"Demonstrate and verify server-authoritative autonomous commerce pipelines against live PostgreSQL persistence."})]}),u.jsx("div",{className:"flex items-center gap-2",children:u.jsxs(dt,{variant:"outline",size:"sm",onClick:()=>A(!0),disabled:v||p,className:"text-xs gap-1.5 bg-[#0D1424] border-[#24314A] text-text-secondary hover:text-text-primary",children:[u.jsx(Dy,{className:"h-3.5 w-3.5"})," Reset Demo Data"]})})]}),P&&u.jsxs("div",{className:"p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl text-xs flex items-center justify-between shadow-glow-success",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx(Wr,{className:"h-4 w-4"}),u.jsx("span",{children:P})]}),u.jsx("button",{onClick:()=>U(null),className:"text-emerald-400 font-bold hover:underline",children:"Dismiss"})]}),x&&u.jsxs("div",{className:"p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl text-xs flex items-center justify-between",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx(ma,{className:"h-4 w-4"}),u.jsx("span",{children:x})]}),u.jsx("button",{onClick:()=>M(null),className:"text-rose-300 font-bold hover:underline",children:"Dismiss"})]}),u.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-3 gap-4",children:[u.jsxs("div",{onClick:()=>e("STANDARD_AUTO_COMMERCE"),className:`glass-panel p-5 rounded-xl cursor-pointer transition-all border-2 ${s==="STANDARD_AUTO_COMMERCE"?"border-brand bg-[#141D31] shadow-glow":"border-[#24314A] bg-[#0D1424]/80 hover:border-brand/40"}`,children:[u.jsxs("div",{className:"flex items-center justify-between mb-3",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx("div",{className:"p-2 rounded-lg bg-brand/15 text-brand-bright",children:u.jsx(ox,{className:"h-4 w-4"})}),u.jsx("span",{className:"font-bold text-xs text-text-primary",children:"Standard Auto Commerce"})]}),u.jsx("span",{className:"text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",children:"ALLOW"})]}),u.jsxs("p",{className:"text-xs text-text-secondary leading-relaxed mb-3",children:["Buyer agent proposes 10% discount. Policy engine evaluates ",u.jsx("strong",{className:"text-text-primary",children:"ALLOW"}),", generates order, and captures Razorpay payment automatically."]}),u.jsx("div",{className:"text-[10px] font-mono bg-[#070B14] p-2.5 rounded-lg border border-[#24314A] text-text-muted",children:"Flow: Discovery → Quote (10% off) → Policy Approved → Order → Razorpay Webhook → Settled"})]}),u.jsxs("div",{onClick:()=>e("HITL_ESCALATION_COMMERCE"),className:`glass-panel p-5 rounded-xl cursor-pointer transition-all border-2 ${s==="HITL_ESCALATION_COMMERCE"?"border-amber-500 bg-[#141D31] shadow-glow-warning":"border-[#24314A] bg-[#0D1424]/80 hover:border-amber-500/40"}`,children:[u.jsxs("div",{className:"flex items-center justify-between mb-3",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx("div",{className:"p-2 rounded-lg bg-amber-500/15 text-amber-400",children:u.jsx(dx,{className:"h-4 w-4"})}),u.jsx("span",{className:"font-bold text-xs text-text-primary",children:"HITL Human Approval"})]}),u.jsx("span",{className:"text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20",children:"ESCALATE"})]}),u.jsxs("p",{className:"text-xs text-text-secondary leading-relaxed mb-3",children:["Buyer agent requests aggressive 20% discount (exceeds 15% limit). Policy engine emits ",u.jsx("strong",{className:"text-text-primary",children:"ESCALATE_APPROVAL"})," and queues a ticket in Approvals."]}),u.jsx("div",{className:"text-[10px] font-mono bg-[#070B14] p-2.5 rounded-lg border border-[#24314A] text-text-muted",children:"Flow: Discovery → Quote (20% off) → Escalated → Pending Ticket → Merchant Approves/Rejects"})]}),u.jsxs("div",{onClick:()=>e("PAYMENT_RECONCILIATION"),className:`glass-panel p-5 rounded-xl cursor-pointer transition-all border-2 ${s==="PAYMENT_RECONCILIATION"?"border-emerald-500 bg-[#141D31] shadow-glow-success":"border-[#24314A] bg-[#0D1424]/80 hover:border-emerald-500/40"}`,children:[u.jsxs("div",{className:"flex items-center justify-between mb-3",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx("div",{className:"p-2 rounded-lg bg-emerald-500/15 text-emerald-400",children:u.jsx(eh,{className:"h-4 w-4"})}),u.jsx("span",{className:"font-bold text-xs text-text-primary",children:"Payment Reconciliation"})]}),u.jsx("span",{className:"text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20",children:"RECOVER"})]}),u.jsx("p",{className:"text-xs text-text-secondary leading-relaxed mb-3",children:"Simulates a dropped webhook scenario. Store operator triggers out-of-band server reconciliation directly against Razorpay API to settle the order."}),u.jsx("div",{className:"text-[10px] font-mono bg-[#070B14] p-2.5 rounded-lg border border-[#24314A] text-text-muted",children:"Flow: Order Pending → Dropped Webhook → Manual Reconcile Trigger → Razorpay Query → Settled"})]})]}),u.jsxs("div",{className:"glass-panel rounded-2xl p-6 border border-[#24314A] bg-[#0D1424]",children:[u.jsxs("div",{className:"flex items-center justify-between mb-4 pb-3 border-b border-[#24314A]/60",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx(Hy,{className:"h-4 w-4 text-brand-bright"}),u.jsx("h3",{className:"text-xs font-mono font-bold uppercase tracking-wider text-text-primary",children:"Simulation Parameters & Engine Control"})]}),u.jsx("span",{className:"text-[11px] font-mono text-text-muted",children:"Server-Authoritative Test Runtime"})]}),u.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-3 gap-4 mb-5",children:[u.jsxs("div",{children:[u.jsx("label",{className:"text-xs font-mono text-text-muted block mb-1.5 uppercase",children:"Target Product SKU"}),u.jsxs("select",{value:t,onChange:R=>r(R.target.value),className:"w-full bg-[#070B14] border border-[#24314A] rounded-xl p-2.5 text-xs text-text-primary focus:outline-none focus:border-brand",children:[u.jsx("option",{value:"RUN-PRO-01",children:"RUN-PRO-01: Apex Carbon Pro (₹12,999)"}),u.jsx("option",{value:"AIR-VEST-02",children:"AIR-VEST-02: AeroFlow Running Vest (₹4,499)"}),u.jsx("option",{value:"PACE-BAND-03",children:"PACE-BAND-03: TempoPulse GPS Sensor (₹7,999)"})]})]}),u.jsxs("div",{children:[u.jsx("label",{className:"text-xs font-mono text-text-muted block mb-1.5 uppercase",children:"Order Quantity"}),u.jsx("input",{type:"number",min:1,max:10,value:o,onChange:R=>l(parseInt(R.target.value)||1),className:"w-full bg-[#070B14] border border-[#24314A] rounded-xl p-2.5 text-xs text-text-primary focus:outline-none focus:border-brand"})]}),u.jsxs("div",{children:[u.jsx("label",{className:"text-xs font-mono text-text-muted block mb-1.5 uppercase",children:"Target Discount Rate (%)"}),u.jsx("input",{type:"number",min:0,max:50,disabled:s==="HITL_ESCALATION_COMMERCE",value:s==="HITL_ESCALATION_COMMERCE"?"20":d,onChange:R=>f(R.target.value),className:"w-full bg-[#070B14] border border-[#24314A] rounded-xl p-2.5 text-xs text-text-primary focus:outline-none focus:border-brand disabled:opacity-50"})]})]}),u.jsxs("div",{className:"flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#24314A]/60",children:[u.jsxs("div",{className:"flex items-center gap-2 text-xs text-text-secondary",children:[u.jsx(xc,{className:"h-4 w-4 text-emerald-400 shrink-0"}),u.jsx("span",{children:"Executes authentic backend state machines, HMAC webhooks, and SHA-256 audit chaining."})]}),u.jsx(dt,{onClick:N,disabled:p,className:"bg-brand hover:bg-brand-deep text-white font-semibold text-xs px-6 shadow-glow",children:p?u.jsxs("span",{className:"flex items-center gap-2",children:[u.jsx("span",{className:"h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"}),"Executing Pipeline..."]}):u.jsxs("span",{className:"flex items-center gap-2",children:[u.jsx(Cy,{className:"h-3.5 w-3.5 fill-current"})," Run Simulation Scenario"]})})]})]}),_&&u.jsxs("div",{className:"space-y-4",children:[u.jsxs("div",{className:`glass-panel p-5 rounded-2xl border text-xs flex flex-col md:flex-row md:items-center justify-between gap-4 ${_.status==="SETTLED"?"border-emerald-500/40 bg-emerald-500/5 shadow-glow-success":"border-amber-500/40 bg-amber-500/5 shadow-glow-warning"}`,children:[u.jsxs("div",{className:"space-y-1.5",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[_.status==="SETTLED"?u.jsx(Wr,{className:"h-5 w-5 text-emerald-400"}):u.jsx(ma,{className:"h-5 w-5 text-amber-400"}),u.jsx("span",{className:"font-bold text-sm text-text-primary",children:_.message})]}),u.jsxs("div",{className:"flex flex-wrap items-center gap-3 text-text-secondary text-xs",children:[u.jsxs("span",{children:["Scenario: ",u.jsx("strong",{className:"text-text-primary",children:_.scenario})]}),u.jsx("span",{children:"•"}),u.jsxs("span",{children:["Subtotal: ",u.jsx("strong",{className:"text-text-primary",children:fn(_.subtotal_paise)})]}),u.jsx("span",{children:"•"}),u.jsxs("span",{children:["Discount: ",u.jsxs("strong",{className:"text-amber-400",children:["-",fn(_.discount_paise)]})]}),u.jsx("span",{children:"•"}),u.jsxs("span",{children:["Settled Total: ",u.jsx("strong",{className:"text-emerald-400 font-bold",children:fn(_.total_paise)})]})]})]}),u.jsxs("div",{className:"flex flex-wrap items-center gap-2",children:[_.approval_id&&u.jsxs("a",{href:"/approvals",className:"px-3.5 py-2 bg-amber-500 text-[#070B14] rounded-xl text-xs font-bold hover:bg-amber-400 transition flex items-center gap-1.5",children:["Resolve in Queue ",u.jsx(yd,{className:"h-3 w-3"})]}),_.order_id&&u.jsxs("a",{href:"/orders",className:"px-3.5 py-2 bg-brand text-white rounded-xl text-xs font-semibold hover:bg-brand-deep transition flex items-center gap-1.5",children:["View Order Ledger ",u.jsx(yd,{className:"h-3 w-3"})]}),u.jsxs("a",{href:"/audit",className:"px-3.5 py-2 bg-[#141D31] text-text-primary border border-[#24314A] rounded-xl text-xs font-medium hover:bg-[#1E293B] transition flex items-center gap-1.5",children:["Audit Evidence ",u.jsx(yd,{className:"h-3 w-3"})]})]})]}),u.jsxs("div",{className:"glass-panel rounded-2xl p-6 border border-[#24314A] bg-[#0D1424]",children:[u.jsxs("div",{className:"flex items-center justify-between mb-4 pb-3 border-b border-[#24314A]/60",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx(oy,{className:"h-4 w-4 text-brand-bright"}),u.jsxs("h3",{className:"text-xs font-mono font-bold uppercase tracking-wider text-text-primary",children:["Deterministic Execution Trace (",_.steps.length," Steps)"]})]}),u.jsxs("span",{className:"font-mono text-[11px] text-text-muted",children:["Policy Hash: ",_.policy_hash.slice(0,16),"..."]})]}),u.jsx("div",{className:"space-y-4",children:_.steps.map(R=>u.jsxs("div",{className:"flex items-start gap-3 relative pb-2 border-l-2 border-[#24314A] pl-4 ml-2 last:border-transparent",children:[u.jsx("div",{className:"absolute -left-[9px] top-0.5 h-4 w-4 rounded-full bg-[#070B14] border-2 border-brand flex items-center justify-center text-[9px] font-bold text-brand-bright",children:R.step_number}),u.jsxs("div",{className:"w-full bg-[#070B14]/80 border border-[#24314A] rounded-xl p-3.5 text-xs space-y-2",children:[u.jsxs("div",{className:"flex items-center justify-between",children:[u.jsxs("div",{className:"flex items-center gap-2",children:[u.jsx("span",{className:"font-bold text-text-primary",children:R.actor}),u.jsxs("span",{className:"font-mono text-[10px] text-brand-bright",children:["[",R.action,"]"]})]}),u.jsx(bn,{variant:R.status==="SETTLED"||R.status==="SUCCESS"?"success":R.status==="ESCALATED"?"warning":"secondary",className:"text-[9px] font-mono",children:R.status})]}),u.jsx("p",{className:"text-text-secondary text-xs",children:R.summary}),R.details&&Object.keys(R.details).length>0&&u.jsx("pre",{className:"text-[11px] font-mono bg-[#0D1424] p-3 rounded-lg border border-[#24314A] text-text-secondary overflow-x-auto",children:JSON.stringify(R.details,null,2)})]})]},R.step_number))})]})]}),u.jsxs(Po,{isOpen:w,onClose:()=>A(!1),title:"Reset & Re-seed Demo Sandbox Data?",description:"This will re-initialize standard test products and restore default policy limits for evaluation.",children:[u.jsx("div",{className:"text-xs text-text-secondary space-y-2 py-2",children:u.jsxs("p",{children:["Standard products (",u.jsx("strong",{className:"text-text-primary",children:"RUN-PRO-01"}),", ",u.jsx("strong",{className:"text-text-primary",children:"AIR-VEST-02"}),", ",u.jsx("strong",{className:"text-text-primary",children:"PACE-BAND-03"}),") and default autonomy bounds (15% max discount, 20% min margin) will be verified and ensured on PostgreSQL."]})}),u.jsxs(MT,{children:[u.jsx(dt,{variant:"outline",size:"sm",onClick:()=>A(!1),className:"text-xs",children:"Cancel"}),u.jsx(dt,{size:"sm",onClick:L,disabled:v,className:"text-xs bg-brand hover:bg-brand-deep text-white",children:v?"Resetting...":"Confirm Reset"})]})]})]})},DT=({onNavigate:s})=>u.jsxs("div",{className:"flex min-h-[calc(100vh-12rem)] flex-col items-center justify-center text-center px-4",children:[u.jsx("div",{className:"flex h-16 w-16 items-center justify-center rounded-2xl bg-destructive/15 text-destructive mb-4",children:u.jsx(fx,{className:"h-8 w-8"})}),u.jsx("h2",{className:"text-2xl font-bold",children:"Access Denied"}),u.jsx("p",{className:"mt-2 max-w-sm text-sm text-muted-foreground",children:"You do not have the required merchant authorization or capability to access this view."}),u.jsxs("div",{className:"mt-6 flex gap-3",children:[u.jsx(dt,{onClick:()=>s("/login"),variant:"primary",size:"sm",children:"Sign In as Admin"}),u.jsx(dt,{onClick:()=>s("/"),variant:"outline",size:"sm",children:"Back to Home"})]})]}),UT=({onNavigate:s})=>u.jsxs("div",{className:"flex min-h-[calc(100vh-12rem)] flex-col items-center justify-center text-center px-4",children:[u.jsx("div",{className:"flex h-16 w-16 items-center justify-center rounded-2xl bg-muted text-muted-foreground mb-4",children:u.jsx(ny,{className:"h-8 w-8"})}),u.jsx("h2",{className:"text-2xl font-bold",children:"404 - View Not Found"}),u.jsx("p",{className:"mt-2 max-w-sm text-sm text-muted-foreground",children:"The requested control plane route does not exist."}),u.jsx(dt,{onClick:()=>s("/"),className:"mt-6",size:"sm",children:"Return Home"})]}),FT=({onNavigate:s})=>{const{isAuthenticated:e,merchant:t}=pr();return u.jsx("header",{className:"sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-md",children:u.jsxs("div",{className:"container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8",children:[u.jsx("div",{className:"flex items-center gap-3 cursor-pointer",onClick:()=>s("/"),children:u.jsx("span",{className:"font-display text-2xl font-semibold tracking-[-0.09em] text-slate-50",children:"pimp"})}),u.jsx("nav",{className:"flex items-center gap-3",children:e?u.jsxs(dt,{onClick:()=>s("/dashboard"),variant:"primary",size:"sm",children:[u.jsx(ux,{className:"h-4 w-4"}),u.jsx("span",{children:(t==null?void 0:t.name)||"Dashboard"})]}):u.jsxs(u.Fragment,{children:[u.jsx(dt,{onClick:()=>s("/login"),variant:"ghost",size:"sm",children:"Log In"}),u.jsxs(dt,{onClick:()=>s("/signup"),variant:"primary",size:"sm",children:["Get Started",u.jsx(cr,{className:"h-4 w-4"})]})]})})]})})},Zg=({currentPath:s,onNavigate:e,children:t})=>{const{merchant:r,logout:o,sessionExpired:l,dismissExpiredDialog:d}=pr(),[f,p]=xe.useState(!1),m=[{title:"OPERATE",items:[{label:"Overview",path:"/dashboard",icon:ux},{label:"Approval Queue",path:"/approvals",icon:Rc},{label:"Orders Ledger",path:"/orders",icon:hx},{label:"Payments",path:"/payments",icon:eh}]},{title:"MANAGE",items:[{label:"Products & Catalog",path:"/catalog",icon:vc},{label:"Inventory Stock",path:"/inventory",icon:cx},{label:"Policy Governance",path:"/policies",icon:px}]},{title:"INSPECT",items:[{label:"Audit Trail (SHA-256)",path:"/audit",icon:th},{label:"Simulation Sandbox",path:"/demo",icon:rf,badge:"Interactive"}]}];return u.jsxs("div",{className:"portal-font flex min-h-screen bg-[#101113] text-[#f3f4f6]",children:[u.jsxs("aside",{className:"hidden w-64 flex-col border-r border-white/10 bg-[#1b1c1e] lg:flex",children:[u.jsx("div",{className:"flex h-16 cursor-pointer items-center gap-3 border-b border-white/10 px-5 transition hover:opacity-90",onClick:()=>e("/"),children:u.jsxs("div",{children:[u.jsx("span",{className:"block text-xl font-semibold tracking-[-0.08em] text-slate-50",children:"pimp"}),u.jsx("span",{className:"text-[10px] text-text-muted font-mono tracking-wide",children:"CONTROL PLANE"})]})}),u.jsx("div",{className:"border-b border-white/[0.07] p-3",children:u.jsxs("div",{className:"rounded-md border border-white/10 bg-white/[0.035] p-3",children:[u.jsxs("div",{className:"flex items-center justify-between mb-1",children:[u.jsx("span",{className:"text-[10px] uppercase font-mono tracking-wider text-brand-bright",children:"Store Profile"}),u.jsxs("span",{className:"inline-flex items-center gap-1 text-[10px] text-emerald-400 font-medium",children:[u.jsx("span",{className:"h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"}),"ACTIVE"]})]}),u.jsx("p",{className:"font-semibold text-xs text-text-primary truncate",children:(r==null?void 0:r.name)||"Store Operator"}),u.jsxs("p",{className:"text-[11px] text-text-muted font-mono truncate",children:["slug: ",(r==null?void 0:r.slug)||"default"]})]})}),u.jsx("nav",{className:"flex-1 space-y-4 p-3 overflow-y-auto",children:m.map(_=>u.jsxs("div",{className:"space-y-1",children:[u.jsx("h3",{className:"px-3 text-[10px] font-mono font-semibold tracking-wider text-text-muted uppercase",children:_.title}),u.jsx("div",{className:"space-y-0.5",children:_.items.map(S=>{const x=S.icon,M=s===S.path;return u.jsxs("button",{onClick:()=>e(S.path),className:`flex w-full items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-all ${M?"bg-white/[0.10] text-white font-semibold":"text-slate-400 hover:bg-white/[0.06] hover:text-slate-100"}`,children:[u.jsxs("div",{className:"flex items-center gap-2.5",children:[u.jsx(x,{className:`h-4 w-4 ${M?"text-emerald-300":"text-slate-500"}`}),u.jsx("span",{children:S.label})]}),S.badge&&u.jsx("span",{className:"px-1.5 py-0.5 rounded text-[9px] font-mono bg-brand/20 text-brand-bright border border-brand/30",children:S.badge})]},S.path)})})]},_.title))}),u.jsxs("div",{className:"space-y-2 border-t border-white/10 bg-black/10 p-3",children:[u.jsxs("div",{className:"flex items-center justify-between text-[10px] text-text-muted px-2 font-mono",children:[u.jsx("span",{children:"Autonomy Level"}),u.jsxs("span",{className:"text-text-primary font-bold",children:["L",(r==null?void 0:r.policies.autonomyLevel)??1]})]}),u.jsxs(dt,{onClick:o,variant:"ghost",size:"sm",className:"w-full justify-start text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10",children:[u.jsx(Ym,{className:"h-3.5 w-3.5"}),u.jsx("span",{children:"Sign Out"})]})]})]}),u.jsxs("div",{className:"flex flex-1 flex-col overflow-hidden",children:[u.jsxs("header",{className:"flex h-16 items-center justify-between border-b border-white/10 bg-[#17181a] px-4 sm:px-6",children:[u.jsxs("div",{className:"flex items-center gap-3",children:[u.jsx("button",{onClick:()=>p(!f),className:"rounded-lg p-2 text-text-muted hover:bg-white/10 hover:text-text-primary lg:hidden",children:f?u.jsx(mx,{className:"h-5 w-5"}):u.jsx(xy,{className:"h-5 w-5"})}),u.jsxs("div",{children:[u.jsx("h1",{className:"text-sm font-bold capitalize text-text-primary flex items-center gap-2",children:s.replace("/","").replace("-"," ")||"Overview Command"}),u.jsx("p",{className:"text-[10px] text-text-muted font-mono hidden sm:block",children:"SERVER-AUTHORITATIVE COMMERCE PIPELINE"})]})]}),u.jsxs("div",{className:"flex items-center gap-3",children:[u.jsxs("div",{className:"hidden items-center gap-1.5 rounded-md border border-white/10 bg-white/[0.035] px-2.5 py-1 text-[11px] text-slate-400 md:flex",children:[u.jsx(Z_,{className:"h-3 w-3 text-emerald-400"}),u.jsx("span",{children:"InsForge PostgreSQL"})]}),u.jsx(bn,{variant:"outline",className:"border-emerald-300/25 bg-emerald-300/[0.06] text-[10px] text-emerald-200",children:"TEST MODE"}),u.jsxs(dt,{onClick:()=>e("/demo"),variant:"outline",size:"sm",className:"hidden border-white/15 bg-white/[0.06] text-xs text-slate-200 hover:bg-white/[0.1] sm:inline-flex",children:[u.jsx(rf,{className:"h-3 w-3 text-brand-bright"}),"Sandbox"]})]})]}),f&&u.jsxs("div",{className:"animate-in slide-in-from-top-2 space-y-4 border-b border-white/10 bg-[#1b1c1e] p-4 lg:hidden",children:[m.map(_=>u.jsxs("div",{className:"space-y-1",children:[u.jsx("h4",{className:"text-[10px] font-mono text-text-muted uppercase px-2",children:_.title}),_.items.map(S=>{const x=S.icon,M=s===S.path;return u.jsxs("button",{onClick:()=>{e(S.path),p(!1)},className:`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium ${M?"bg-emerald-300 text-slate-950 font-semibold":"text-text-secondary hover:bg-white/[0.07]"}`,children:[u.jsx(x,{className:"h-4 w-4"}),u.jsx("span",{children:S.label})]},S.path)})]},_.title)),u.jsxs(dt,{onClick:o,variant:"ghost",size:"sm",className:"w-full justify-start text-rose-400 hover:bg-rose-500/10 text-xs",children:[u.jsx(Ym,{className:"h-3.5 w-3.5"}),"Sign Out"]})]}),u.jsx("main",{className:"flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8",children:u.jsx("div",{className:"container mx-auto max-w-7xl",children:t})})]}),l&&u.jsxs(Po,{isOpen:l,onClose:d,title:"Session Expired",description:"Your merchant admin credentials have expired. Please sign in again to continue managing your autonomous store.",children:[u.jsx("div",{className:"py-4 text-xs text-text-secondary",children:"For security, administrator tokens are bounded to 24 hours. No unauthorized financial operations can proceed without re-authentication."}),u.jsx("div",{className:"flex justify-end gap-3",children:u.jsx(dt,{onClick:()=>{d(),e("/login")},className:"w-full",children:"Sign In Again"})})]})]})},kT=()=>u.jsx("footer",{className:"border-t border-border bg-card/20 py-8 text-xs text-muted-foreground",children:u.jsxs("div",{className:"container mx-auto flex flex-col sm:flex-row max-w-7xl items-center justify-between gap-4 px-4 sm:px-6",children:[u.jsx("span",{className:"font-display text-base font-semibold tracking-[-0.07em] text-slate-100",children:"pimp"}),u.jsxs("div",{className:"flex items-center gap-6",children:[u.jsx("a",{href:"/docs",className:"hover:text-foreground transition-colors",children:"API Docs"}),u.jsx("a",{href:"https://razorpay.com",target:"_blank",rel:"noreferrer",className:"hover:text-foreground transition-colors",children:"Razorpay Powered"}),u.jsx("span",{className:"font-mono",children:"Protocol: 2026-03-01"})]})]})}),OT=()=>{const{isAuthenticated:s,isLoading:e}=pr(),[t,r]=xe.useState(()=>window.location.pathname||"/");xe.useEffect(()=>{const d=()=>{r(window.location.pathname||"/")};return window.addEventListener("popstate",d),()=>window.removeEventListener("popstate",d)},[]);const o=d=>{window.history.pushState({},"",d),r(d),typeof window<"u"&&window.scrollTo&&window.scrollTo(0,0)};if(e)return u.jsx("div",{className:"flex h-screen w-screen items-center justify-center bg-background text-primary",children:u.jsx("div",{className:"h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"})});if(t==="/")return u.jsxs("div",{className:"min-h-screen flex flex-col",children:[u.jsx(FT,{onNavigate:o}),u.jsx("main",{className:"flex-1",children:u.jsx(gT,{onNavigate:o})}),u.jsx(kT,{})]});if(t==="/login")return s?(o("/dashboard"),null):u.jsx(xT,{onNavigate:o});if(t==="/signup")return s?(o("/dashboard"),null):u.jsx(vT,{onNavigate:o});if(!s)return o("/login"),null;if(t==="/onboarding")return u.jsx(Zg,{currentPath:t,onNavigate:o,children:u.jsx(yT,{onNavigate:o})});const l=()=>{switch(t){case"/dashboard":return u.jsx(ST,{onNavigate:o});case"/catalog":return u.jsx(bT,{});case"/inventory":return u.jsx(ET,{});case"/quotes":return u.jsx(wT,{});case"/orders":return u.jsx(TT,{});case"/payments":return u.jsx(AT,{});case"/negotiations":return u.jsx(CT,{});case"/approvals":return u.jsx(NT,{});case"/policies":return u.jsx(RT,{});case"/audit":return u.jsx(PT,{});case"/settings":return u.jsx(LT,{});case"/demo":return u.jsx(IT,{});case"/unauthorized":return u.jsx(DT,{onNavigate:o});default:return u.jsx(UT,{onNavigate:o})}};return u.jsx(Zg,{currentPath:t,onNavigate:o,children:l()})},zT=()=>u.jsx(Xv,{children:u.jsx(OT,{})});Gv.createRoot(document.getElementById("root")).render(u.jsx(Nc.StrictMode,{children:u.jsx(zT,{})}));
