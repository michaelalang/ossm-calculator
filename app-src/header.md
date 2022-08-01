<style>
td, th {
   border: 1px solid black;
   padding: 2px;
}
table {
   width: 45%;
   border-collapse: collapse;
}
</style>


# OpenShift Service Mesh (OSSM) size calculator

This calculator uses the formula documented at [https://docs.openshift.com/container-platform/4.10/service_mesh/v2x/ossm-performance-scalability.html](ossm-performance-scalability.html) to provide an overhead in memory and cpu when populating OSSM

## Technical description for the Matrix

Mandatory requirements:

- Namespace/pod specifications on 
    - requests vcpu
    - requests memory
    - limit vcpu 
    - limit memory

The calucaltion is based from the example Load test on 
- 1000 services
- 2000 sidecards
- 70000 mesh-wide requests

Breaking this down into:

- Control Plane overhead
    - 0.001 vcpu
    - 805306 B memory
- Envoy Proxy overhead
    - 0.00035 vcpu/request
    - 41943 B memory/request
- Telemetry overhead
    - 0.0006 vcpu/request


