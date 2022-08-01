# OpenShift Service Mesh (OSSM) calulator

This little tool is ment to support your calculation on growing a mesh by calculating the overhead added for each service in the Mesh.

## howto build the image

The image used the s2i ubi/python3.9 image as base image.
Python dependencies added to generate some kind of web output:

- gunicorn
- Flask
- markdown
- pandas
- PYyaml
- tabulate

~~~
$ podman build -t ossm-calculator .
STEP 1/9: FROM registry.access.redhat.com/ubi8/python-39
STEP 2/9: USER 0
--> 2a12474ff33
STEP 3/9: ADD app-src /tmp/src
[... output omitted ...]

Successfully tagged <your-image-tag-name>
0477b610432c348b274d98c82a019ff0d0c04ee17f9cb70e5172c6f4672ca31d
~~~

## running the calculator image

The s2i image populates by default port 8080. There's no additional resource needed to run the image.

- using podman
~~~
$ podman run -d --rm --name ossm-calculator -p 8080:8080 ossm-calculator
~~~

- using openshift deployment
~~~
$ oc new-app --strategy=docker https://github.com/michaelalang/ossm-calculator.git 
$ oc expose service ossm-calculator
~~~

## using the calculator image

- access the calculator at http://localhost:8080
- manual calculation 
    - enter the service count you expect to deploy 
    - enter the sidecars count you expect to deploy (1/Service, 1/Deployment)
    - enter the requests you want to be able to handle
    - enter the replicas you expect to scale the deployments
    - enter the average vcpu request definition
    - enter the average memory request definition
    - hit **Submit**
- OpenShift based calculation
    - create an _all_ deployments data file
    ~~~
    $ oc get deployment -A -o yaml > /tmp/deployments.yml
    ~~~
    - create a selective deployments data file
    ~~~
    $ for p in $(oc get projects --no-headers=true | grep -v openshift) ; do oc -n ${p} get deployment -o yaml >> /tmp/deployments.yml ; echo "---" >> /tmp/deployments.yml;  done
    ~~~
    - enter the requests you want to be able to handle
    - select **Choose file**
        - nagivate and select _/tmp/deployments.yml_
    - select **Submitt**

