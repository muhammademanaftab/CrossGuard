/**
 * Edge Case: Minified Code
 * Tests detection in minified/compressed JavaScript
 *
 * Expected features: const, let, arrow-functions, promises, fetch,
 * queryselector, classlist, json, addeventlistener
 */

// Minified code simulation (no whitespace, short variable names)
const a=document.querySelector(".app"),b=()=>fetch("/api").then(r=>r.json()),c=async()=>{const d=await b();a.classList.add("loaded");return d};document.addEventListener("DOMContentLoaded",()=>{c().then(e=>{localStorage.setItem("data",JSON.stringify(e))})});

// More minified patterns
const f=()=>{let g=0;return{inc:()=>++g,get:()=>g}};const h=new Promise((i,j)=>{setTimeout(()=>i("done"),100)});h.then(k=>console.log(k));

// Minified class
class L{constructor(m){this.n=m}o(p){return this.n+p}}const q=new L(10);

// Arrow functions in minified form
const r=a=>a*2,s=(a,b)=>a+b,t=async a=>await fetch(a),u=()=>{};

// Chained methods minified
document.querySelectorAll(".item").forEach(v=>{v.classList.toggle("active");v.addEventListener("click",w=>{w.preventDefault();v.dataset.clicked="true"})});

// Async/await minified
(async()=>{try{const x=await fetch("/data");const y=await x.json();return y}catch(z){console.error(z)}})();
