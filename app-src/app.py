#!/usr/bin/python3

import json
import yaml
from flask import Flask, jsonify, make_response, request
import markdown
import os
import pandas as pd
from calculator import *

markdown_extensions = [
    'tables', 'extra',
    'attr_list', 'def_list',
    'fenced_code', 'footnotes',
    'codehilite', 'legacy_attrs',
    'meta', 'smarty', 'toc',
    'wikilinks'
    ]

def get_queryform():
    query = ['<form action="/index.html" method="POST" enctype="multipart/form-data">']
    for name, display in zip(('srv', 'scar', 'req', 'pods', 'vcpu', 'memory'),
                             ('Services', 'Sidecars', 'Mesh-wide Requests', 'Pod count/service', 'vcpu requests', 'memory requests (GB)')):
        query.append('<label for="%s">%s:</label>' % (name, display))
        query.append('<input id="%s" name="%s" value="1"/><br/>' % (name, name))
    query.append('<input type="file" name="ocyaml" />')
    query.append('<input type="submit" value="Submit">')
    query.append('</form>')
    return '\n'.join(query)

app = Flask(__name__)

def resources_from_yaml(dCP=None, dDP=None, data=None):
    app.logger.debug('entering resources_from_yaml')
    data = yaml.safe_load_all(data)
    for namespace in data:
        if namespace == None:    continue
        for deployment in namespace.get('items', []):
            app.logger.info('doing %s' % deployment.get('metadata').get('name'))
            REPLICAS = deployment.get('spec', {}).get('replicas', 1)
            for container in deployment.get('spec', {}).get('template',{}).get('spec',{}).get('containers',[]):
                req = container.get('resources', {})
                if req == {}:
                    # assuming some defaults
                    #app.logger.info('assuming defaults for %s' % deployment.get('metadata').get('name'))
                    #dCP.append(Service(vcpu=0.1, memory=64 * 2**20, size=1, overhead=dDP))
                    continue
                else:
                    if req.get('requests').get('memory').endswith('Gi'): MEM = 2**30
                    if req.get('requests').get('memory').endswith('Mi'): MEM = 2**20
                    if req.get('requests').get('cpu').endswith('m'):     CPU = int(req.get('requests').get('cpu')[:-1]) / 100
                    else:                                CPU = int(req.get('requests').get('cpu'))
                    app.logger.debug('Adding %s %s %s\n' % (CPU, req.get('requests').get('memory'), MEM))
                    dCP.append(Service(vcpu=CPU, memory=int(req.get('requests').get('memory')[:-2]) * MEM, size=REPLICAS, overhead=dDP))
    return (dCP, dDP)

@app.route('/health')
def health():
    return jsonify(dict(state='ok')), 200
	
@app.route('/index.html', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    header = open('header.md').read()
    queryform = get_queryform()
    rsp = ''
    footer = open('footer.md').read()
    ossm_services = int(request.form.get('srv', 1000))
    ossm_sidecars = int(request.form.get('scar', 2000))
    ossm_requests = int(request.form.get('req', 70000))
    ossm_size     = int(request.form.get('pods', 1))
    ossm_vcpu     = float(request.form.get('vcpu', 0.1))
    ossm_memory   = float(request.form.get('memory', 0.125)) # GB
    C = CP(sidecars=ossm_sidecars,
           requests=ossm_requests)
    D = DP(requests=ossm_requests)
    app.logger.debug('request: %s' % request)
    if request.method == 'POST':
        try:
            if request.files['ocyaml'].filename == '':
                raise TypeError('no yaml provided')
            app.logger.info('loading resources_from_yaml')
            C, D = resources_from_yaml(dCP=CP(sidecars=0,requests=ossm_requests),
                                       dDP=DP(requests=ossm_requests), data=request.files['ocyaml'])
        except TypeError as e:
            app.logger.debug(str(e))
            for s in range(0, ossm_services):
                C.append(Service(vcpu=ossm_vcpu, memory=ossm_memory * GB, size=ossm_size, overhead=D))
        C.estimate(GB)
        app.logger.debug(C.sidecars)
        app.logger.debug(C.to_dict())
        df = pd.DataFrame.from_dict(C.to_dict()).fillna(0)
        rsp += df.to_markdown(tablefmt="html")
    if request.args.get('style', False) == 'raw':
        rsp = make_response(str(header + queryform + footer))
        rsp.mimetype = 'text/plain'
    else:
        rsp = make_response(markdown.markdown(str(header + queryform + "\n\n%s\n\n\n" % rsp + footer),
                            extensions=markdown_extensions,
                            output_format='html5'))
    return rsp, 200


if __name__ == '__main__':
    app.debug = False
    app.run(host=os.environ.get('ADDRESS', '0.0.0.0'),
            port=int(os.environ.get('PORT', 8888)),
            threaded=True)
