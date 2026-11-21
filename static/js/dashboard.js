const $ = (id) => document.getElementById(id);
const sections = ["overview","bookings","tickets","sensors","approvals"];
function showSection(name) {
  sections.forEach(id => $(id).classList.toggle("active", id === name));
  document.querySelectorAll(".nav-link").forEach(a => a.classList.toggle("active", a.dataset.section === name));
  const titles = {overview:"Campus overview",bookings:"Room bookings",tickets:"Maintenance tickets",sensors:"Sensor monitoring",approvals:"Approval workflow"};
  $("page-title").textContent = titles[name];
  $("crumb").textContent = name.replace("-", " ").toUpperCase();
  if(name === "bookings") loadBookings();
  if(name === "tickets") loadTickets();
  location.hash = name;
}
document.querySelectorAll(".nav-link").forEach(a => a.addEventListener("click", e => {e.preventDefault();showSection(a.dataset.section)}));
$("today").textContent = new Date().toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric",year:"numeric"});
function showMessage(id, text, ok) { const el=$(id); el.textContent=text; el.className="form-message "+(ok?"success":"error"); }
function table(headers, rows) {
  if(!rows.length) return '<div class="empty">No records yet. Add your first record using the form.</div>';
  return '<table class="data-table"><thead><tr>'+headers.map(h=>`<th>${h}</th>`).join("")+'</tr></thead><tbody>'+
    rows.map(row=>'<tr>'+row.map(v=>`<td>${escapeHtml(String(v ?? ""))}</td>`).join("")+'</tr>').join("")+'</tbody></table>';
}
function escapeHtml(value){return value.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function loadBookings(){
  try{
    const r=await fetch("/api/bookings"); const data=await r.json();
    $("booking-count").textContent=data.length;
    const rows=data.map(b=>[b.room,b.user,b.start.replace("T"," "),b.end.replace("T"," ")]);
    $("booking-table").innerHTML=table(["ROOM","BOOKED BY","START","END"],rows);
    $("recent-bookings").innerHTML=table(["ROOM","BOOKED BY","START"],data.slice(-4).reverse().map(b=>[b.room,b.user,b.start.replace("T"," ")]));
  }catch(e){$("booking-table").textContent="Could not load booking records.";}
}
async function loadTickets(){
  // The starter API creates tickets; the list endpoint is intentionally not exposed yet.
  $("ticket-table").innerHTML='<div class="empty">Ticket creation is available. Ticket listing can be added as an extension.</div>';
}
$("booking-form").addEventListener("submit",async e=>{
  e.preventDefault(); const d=Object.fromEntries(new FormData(e.target).entries());
  try{const r=await fetch("/api/bookings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});const data=await r.json();
    showMessage("booking-message",r.ok?"Booking created successfully.":data.error,!(!r.ok)); if(r.ok){e.target.reset();loadBookings();}
  }catch(err){showMessage("booking-message","Unable to connect to the server.",false);}
});
$("ticket-form").addEventListener("submit",async e=>{
  e.preventDefault();const d=Object.fromEntries(new FormData(e.target).entries());
  try{const r=await fetch("/api/tickets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});const data=await r.json();
    showMessage("ticket-message",r.ok?(data.duplicate?"Duplicate request detected; existing ticket retained.":"Ticket created successfully."):(data.error||"Request failed."),r.ok);if(r.ok)e.target.reset();
  }catch(err){showMessage("ticket-message","Unable to connect to the server.",false);}
});
$("sensor-form").addEventListener("submit",async e=>{
  e.preventDefault();const value=Number(new FormData(e.target).get("value"));
  const r=await fetch("/api/sensors/check",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({value})});const d=await r.json();
  showMessage("sensor-message",d.error|| (d.alert?"Alert: reading has reached the configured threshold.":"Normal: reading is below the threshold."),!d.error);
});
$("approval-form").addEventListener("submit",async e=>{
  e.preventDefault();const f=new FormData(e.target);
  const role=f.get("role"),restricted=f.get("restricted")==="on";
  const r=await fetch("/api/approvals",{method:"POST",headers:{"Content-Type":"application/json","X-Role":role},body:JSON.stringify({restricted})});const d=await r.json();
  showMessage("approval-message",d.message||d.error,r.ok);
});
loadBookings();
if(location.hash && sections.includes(location.hash.slice(1))) showSection(location.hash.slice(1));
