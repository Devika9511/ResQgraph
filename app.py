import streamlit as st

from database.connection import get_driver, verify_connection
from services.incident_service import create_incident, get_dashboard_stats, get_incident, get_recent_incidents, get_locations
from services.response_service import find_best_response
from services.route_service import get_response_graph

st.set_page_config(page_title="ResQGraph", page_icon="🚨", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:1250px}
.hero{padding:30px 32px;border-radius:20px;color:white;background:linear-gradient(135deg,#111827 0%,#1f2937 50%,#4c1d3f 100%);margin-bottom:24px;box-shadow:0 10px 30px rgba(0,0,0,.12)}
.hero h1{margin:0;font-size:2.4rem;font-weight:800}.hero p{margin:8px 0 0;color:#d1d5db;font-size:1rem}
.section-title{font-size:1.35rem;font-weight:800;color:#111827;margin-top:22px;margin-bottom:12px}
.sidebar-brand{font-size:1.2rem;font-weight:800;color:#111827;margin-bottom:5px}.sidebar-description{color:#6b7280;font-size:.82rem;line-height:1.45}.sidebar-powered{color:#6b7280;font-size:.78rem;line-height:1.5;margin-top:15px}
.footer{text-align:center;color:#9ca3af;font-size:.8rem;padding:25px 0 5px;border-top:1px solid #e5e7eb;margin-top:35px}.stButton>button{border-radius:10px;font-weight:700}
</style>
""", unsafe_allow_html=True)


def safe_float(value, default=0.0):
    try:
        return default if value is None else float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return default if value is None else int(value)
    except (TypeError, ValueError):
        return default


def clean_graphviz_dot(dot):
    """Convert double-escaped Graphviz newlines to Graphviz newline escapes."""
    if not dot:
        return dot
    return str(dot).replace("\\\\n", "\\n")


def render_kpi(container, icon, label, value):
    with container:
        with st.container(border=True):
            st.markdown(f"### {icon} {label}")
            st.metric(label="", value=value)


def render_resource_card(container, title, resource_type, details, icon):
    with container:
        with st.container(border=True):
            st.markdown(f"### {icon} {title}")
            st.markdown(f"**{resource_type}**")
            for label, value in details:
                st.markdown(f"**{label}:** {value}")


@st.cache_resource
def db_driver():
    return get_driver()


def connected():
    try:
        return verify_connection(db_driver())
    except Exception:
        return False


try:
    driver = db_driver()
except Exception as exc:
    st.error("Could not initialize the CognoDB connection.")
    st.exception(exc)
    st.stop()

if not connected():
    st.markdown("""
    <div class="hero"><h1>🚨 ResQGraph</h1><p>Emergency Resource Discovery & Response Network</p></div>
    """, unsafe_allow_html=True)
    st.error("ResQGraph cannot reach CognoDB.")
    st.markdown("""
    Check the following configuration:
    - `COGNODB_URI`
    - `COGNODB_USERNAME`
    - `COGNODB_PASSWORD`
    - Confirm that the CognoDB instance is running.
    """)
    st.stop()

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">🚨 ResQGraph</div>
    <div class="sidebar-description">Emergency Resource Discovery & Response Network</div>
    """, unsafe_allow_html=True)
    st.markdown("### Navigation")
    page = st.radio("Navigation", ["Dashboard", "Create Incident", "Response Planner", "Network Explorer"], label_visibility="collapsed")
    st.divider()
    


if page == "Dashboard":
    st.markdown("""
    <div class="hero"><h1>🚨 ResQGraph</h1><p>Discover connected emergency resources and response paths through graph traversal.</p></div>
    """, unsafe_allow_html=True)
    try:
        stats = get_dashboard_stats(driver)
    except Exception as exc:
        st.error("Could not load dashboard statistics."); st.exception(exc); st.stop()
    cols = st.columns(5)
    for col, (icon, label, value) in zip(cols, [
        ("🚨", "Incidents", stats.get("incidents", 0)),
        ("🏥", "Hospitals", stats.get("hospitals", 0)),
        ("🚑", "Ambulances", stats.get("ambulances", 0)),
        ("👨‍⚕️", "Responders", stats.get("responders", 0)),
        ("📍", "Locations", stats.get("locations", 0)),
    ]):
        render_kpi(col, icon, label, value)
    st.markdown('<div class="section-title">Why a graph?</div>', unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        with st.container(border=True):
            st.markdown("### 📍 Network Traversal"); st.write("Follow connected locations and roads to discover reachable emergency resources.")
    with b:
        with st.container(border=True):
            st.markdown("### 🏥 Capability Matching"); st.write("Match incident requirements with hospital specialties and responder qualifications.")
    with c:
        with st.container(border=True):
            st.markdown("### 🚑 Resource Discovery"); st.write("Find available ambulances and emergency teams connected to an incident.")
    st.markdown('<div class="section-title">Recent Incidents</div>', unsafe_allow_html=True)
    try:
        recent=get_recent_incidents(driver,10)
    except Exception as exc:
        st.error("Could not load recent incidents."); st.exception(exc); recent=[]
    if recent:
        for row in recent:
            if row.get("created_at") is not None: row["created_at"]=str(row["created_at"])
        st.dataframe(recent,width="stretch",hide_index=True)
    else: st.info("No incidents yet. Create the first incident from the sidebar.")


elif page == "Create Incident":
    st.markdown("""
    <div class="hero"><h1>🚨 Create Incident</h1><p>Register an emergency incident and connect it to the graph network.</p></div>
    """, unsafe_allow_html=True)
    try: locations=get_locations(driver)
    except Exception as exc: st.error("Could not load locations."); st.exception(exc); st.stop()
    if not locations: st.warning("No locations are available. Run the seed script first."); st.stop()
    with st.form("create_incident"):
        c1,c2=st.columns(2)
        with c1: incident_type=st.selectbox("Incident Type",["Medical Emergency","Road Accident","Fire","Cardiac Emergency","Traffic Collision"])
        with c2: severity=st.selectbox("Severity",["Low","Medium","High","Critical"],index=2)
        location=st.selectbox("Incident Location",[x["name"] for x in locations])
        specialty=st.selectbox("Required Specialty",["Emergency Medicine","Trauma","Cardiology","Burn Care"])
        description=st.text_area("Description",placeholder="Example: Vehicle collision with two injured people.")
        submitted=st.form_submit_button("🚨 Create Incident",width="stretch",type="primary")
    if submitted:
        try:
            result=create_incident(driver,incident_type,severity,location,specialty,description)
            st.success(f"Incident {result['id']} created successfully.")
            st.session_state["selected_incident"]=result["id"]
            st.info("Open Response Planner to generate the connected response.")
        except Exception as exc: st.error(f"Could not create incident: {exc}")


elif page == "Response Planner":
    st.markdown("""
    <div class="hero"><h1>🧭 Response Planner</h1><p>Find an ambulance, qualified responder and suitable hospital through the graph.</p></div>
    """, unsafe_allow_html=True)
    try: incidents=get_recent_incidents(driver,50)
    except Exception as exc: st.error("Could not load incidents."); st.exception(exc); st.stop()
    if not incidents: st.info("No incidents exist. Create one first."); st.stop()
    options={f"{x['id']} • {x['type']} • {x['location']}":x["id"] for x in incidents}
    labels=list(options.keys()); saved=st.session_state.get("selected_incident")
    index=next((i for i,v in enumerate(options.values()) if v==saved),0)
    selected_label=st.selectbox("Incident",labels,index=index); incident_id=options[selected_label]
    incident=get_incident(driver,incident_id)
    if not incident: st.error("The selected incident could not be found."); st.stop()
    st.markdown('<div class="section-title">Incident Summary</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    cols[0].metric("Severity",incident.get("severity","Unknown")); cols[1].metric("Location",incident.get("location","Unknown")); cols[2].metric("Specialty",incident.get("specialty","Unknown")); cols[3].metric("Status",incident.get("status","Unknown"))
    if st.button("🔎 Find Best Response",width="stretch",type="primary"):
        with st.spinner("Traversing the emergency network..."):
            try: response=find_best_response(driver,incident_id)
            except Exception as exc: st.error(f"Response search failed: {exc}"); st.stop()
        if not response or not any(response.values()): st.warning("No suitable connected response resources were found."); st.stop()
        st.success("Response plan generated from the graph.")
        ambulance=response.get("ambulance"); responder=response.get("responder"); hospital=response.get("hospital")
        a,b,c=st.columns(3)
        if ambulance:
            render_resource_card(a,ambulance.get("name","Unknown"),ambulance.get("vehicle_type","Ambulance"),[("Arrival",f"{safe_float(ambulance.get('travel_time_min')):.0f} min"),("Distance",f"{safe_float(ambulance.get('distance_km')):.1f} km"),("Network hops",safe_int(ambulance.get("hops")))],"🚑")
        else:
            with a: st.markdown("### 🚑 Ambulance"); st.warning("No available ambulance found.")
        if responder:
            render_resource_card(b,responder.get("name","Unknown"),responder.get("role","Responder"),[("Qualification",responder.get("specialty","Unknown")),("Connection hops",safe_int(responder.get("hops")))],"👨‍⚕️")
        else:
            with b: st.markdown("### 👨‍⚕️ Responder"); st.warning("No qualified connected responder found.")
        if hospital:
            render_resource_card(c,hospital.get("name","Unknown"),hospital.get("specialty","Hospital"),[("Beds available",safe_int(hospital.get("available_beds"))),("Route",f"{safe_float(hospital.get('travel_time_min')):.0f} min"),("Distance",f"{safe_float(hospital.get('distance_km')):.1f} km"),("Network hops",safe_int(hospital.get("hops")))],"🏥")
        else:
            with c: st.markdown("### 🏥 Hospital"); st.warning("No suitable connected hospital found.")
        st.markdown('<div class="section-title">🗺️ Response Network</div>',unsafe_allow_html=True)
        st.caption("Graph traversal used to identify the response path.")
        try: graph_rows=get_response_graph(driver,incident_id)
        except Exception as exc: st.error("Could not generate the response graph."); st.exception(exc); graph_rows=[]
        if graph_rows:
            dot=clean_graphviz_dot(graph_rows[0].get("dot",""))
            if dot: st.graphviz_chart(dot,width="stretch")
            else: st.info("The response path was found, but no graph visualization data was returned.")
        else: st.info("No graph path is available for visualization.")


elif page == "Network Explorer":
    st.markdown("""
    <div class="hero"><h1>🗺️ Network Explorer</h1><p>Explore the location network and emergency resources stored in CognoDB.</p></div>
    """, unsafe_allow_html=True)
    try: locations=get_locations(driver)
    except Exception as exc: st.error("Could not load locations."); st.exception(exc); st.stop()
    if not locations: st.info("No locations found."); st.stop()
    selected=st.selectbox("Choose a location",[x["name"] for x in locations])
    location_id=next(x["id"] for x in locations if x["name"]==selected)
    try:
        with driver.session() as session:
            result=session.run("""
                MATCH (l:Location {id:$location_id})
                OPTIONAL MATCH (l)-[r:CONNECTED_TO]-(neighbor:Location)
                RETURN l.name AS location, collect({name: neighbor.name, distance_km: r.distance_km, travel_time_min: r.travel_time_min}) AS neighbors
            """,location_id=location_id).single()
    except Exception as exc: st.error("Could not query the location network."); st.exception(exc); st.stop()
    if result:
        st.markdown(f'<div class="section-title">📍 {result["location"]}</div>',unsafe_allow_html=True)
        neighbors=[dict(x) for x in result["neighbors"] if x["name"] is not None]
        if neighbors: st.dataframe(neighbors,width="stretch",hide_index=True)
        else: st.info("This location has no connected neighbors.")

