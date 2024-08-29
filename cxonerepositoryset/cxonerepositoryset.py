import os
import sys
if not getattr(sys, 'frozen', False) :
    sys.path.insert(1, os.path.abspath(os.path.dirname(__file__)) + os.sep + '..' + os.sep + 'shared')
from baserunner import baserunner
from cxloghandler import cxlogger
from datetime import datetime
from src.cxonerepositoryset import cxonereposetconfiguration
from cxoneconn import cxoneconn


class cxonereposet(baserunner) :
    
    # Overriding
    def printhelp(self) :
        print( '============================================================' )
        print( 'CheckmarxOne Repository Set Tool' )
        print( '© Checkmarx. All rights reserved.' )
        print( 'Version: ' + self.config.value('version') )
        print( '============================================================' )
        print( 'PARAMETERS: ')
        print( '  --projid                The project to update, given its id (projname or scanid can be used instead)' )
        print( '  --projname              The project to update, given its name (projid or scanid can be used instead)' )
        print( '  --scanid                The project to update, given a scan id (projid or projname can be used instead)' )
        print( '  --reponame              The repository url to set in the project (mandatory)' )
        print( '  --repobranch            The repository branch to set in the project (mandatory)' )
        print( '  --repotoken             The repositori access token, PAT, to set in the project (mandatory)' )
        print( 'CXONE CONNECTION PARAMETERS:' )
        print( '  --cxone.url             Your CXONE api, example: https//eu.ast.checkmarx.com (mandatory for cxone)' )
        print( '  --cxone.acl             Your CXONE iam, example: https//eu.iam.checkmarx.com (mandatory for cxone)' )
        print( '  --cxone.tenant          Your CXONE tenant name (mandatory for cxone)' )
        print( '  --cxone.apikey          Api key to access your CXONE (mandatory for cxone)' )
        print( '  --cxone.clientid        Client id to access your CXONE' )
        print( '  --cxone.grattype        Grant type to access your CXONE')
        print( '  --cxone.proxy_url       Network proxy to use, optional')
        print( '  --cxone.proxy_username  User name to pass the proxy, if needed' )
        print( '  --cxone.proxy_password  Password to pass the proxy, if needed' )
        print( 'GENERAL OPTIONS:' )
        print( '  --help, -h              This help information' )
        print( '  --verbose, -v           Verbose the execution to the console' )
    
    
    def __resolve_project_id( self, cxone: cxoneconn, projid: str, projname: str, scanid: str ) :
        pid = None
        # Try with the project id
        if not pid and projid :
            data = cxone.cxone.get( '/api/projects/' + str(projid) )
            if data and 'id' in data :
                pid = data['id']
        # Try with the project name
        if not pid and projname :
            data = cxone.cxone.get( '/api/projects?names=' + str(projname) )
            if data and data['projects'] and len(data['projects']) == 1 :
                pid = data['projects'][0]['id']
        # Try with the scan id
        if not pid and scanid :
            data = cxone.cxone.get( '/api/scans/' + str(scanid) )
            if data and 'projectId' in data :
                pid = data['projectId']
        return pid
    
    
    def __update_project( self, cxone: cxoneconn, pid: str, reponame: str, repobranch: str, repotoken: str ) :
        patches = []
        if reponame :
            patch = { 'key': 'scan.handler.git.repository',
                    'name': 'repository',
                    'category': 'git',
                    'originLevel': 'Project',
                    'value': str(reponame),
                    'valuetype': 'String',
                    'allowOverride': True }
            patches.append(patch)
        if repobranch :
            patch = { 'key': 'scan.handler.git.branch',
                    'name': 'branch',
                    'category': 'git',
                    'originLevel': 'Project',
                    'value': str(repobranch),
                    'valuetype': 'String',
                    'allowOverride': True }
            patches.append(patch)
        if repotoken :
            patch = { 'key': 'scan.handler.git.token',
                    'name': 'token',
                    'category': 'git',
                    'originLevel': 'Project',
                    'value': str(repotoken),
                    'valuetype': 'Secret',
                    'allowOverride': True }
            patches.append(patch)
        cxone.cxone.patch( '/api/configuration/project?project-id=' + str(pid), patches )
    
    
    # Overriding
    def execute(self) :
        errorcount = 0
        # Load configurations           
        self.loadconfig( defaults = cxonereposetconfiguration )
        # Init log and verbose
        cxlogger.activate( verbose = self.verbose, logging = True, debug = False )
        # To compute duration
        dtini = datetime.now()
        
        try :
        
            # Check missing params from env variables, with cli options ...
            if not self.config.value('cxone.url') :
                self.config.putvalue( 'cxone.url', None, 'CX_BASE_URI' )
            if not self.config.value('cxone.acl') :
                self.config.putvalue( 'cxone.acl', None, 'CX_BASE_IAM_URI' )
            if not self.config.value('cxone.tenant') :
                self.config.putvalue( 'cxone.tenant', None, 'CX_TENANT' )
            if not self.config.value('cxone.apikey') :
                self.config.putvalue( 'cxone.apikey', None, 'CX_CLIENT_SECRET' )
            if not self.config.value('cxone.clientid') or self.config.value('cxone.clientid') == 'ast-app' :
                xval = os.getenv('CX_CLIENT_ID')
                if xval :
                    self.config.putvalue( 'cxone.clientid', xval )
                    if xval != 'ast-app' :
                        self.config.putvalue( 'cxone.granttype', 'client_credentials' )
        
            projid      = self.config.value('projid')
            projname    = self.config.value('projname')
            scanid      = self.config.value('scanid')
            reponame    = self.config.value('repository')
            repobranch  = self.config.value('branch')
            repotoken   = self.config.value('repotoken')
            
            # Ensure we can identify the project
            if not (projid or projname or scanid) :
                raise Exception( 'Please provide one of "projid", "projname" or "scanid" to identify your project' )
            # Ensure we have required repository data
            if not (reponame and repobranch and repotoken) :
                raise Exception( 'Please provide all "repository", "branch", and "repotoken" to identify your repository' )
            
            # Connect to target CXONE
            try :
                cxlogger.verbose( 'Connecting to CXONE "' + self.config.value('cxone.url') + '"' )
                cxxoneconn = cxoneconn( self.config.value('cxone.url'), self.config.value('cxone.tenant'), self.config.value('cxone.apikey'), 
                                        self.config.value('cxone.acl'), self.config.value('cxone.clientid'), self.config.value('cxone.granttype'), 
                                        self.config.value('cxone.proxy_url'), self.config.value('cxone.proxy_username'), self.config.value('cxone.proxy_password') )
                cxxoneconn.logon()
                ver = cxxoneconn.versionstring
                cxlogger.verbose( 'Connected to CXONE, version ' + ver )
            except Exception as e:
                errorcount += 1
                raise Exception( 'Failed connecting to CXONE with "' + str(e) + '"', True, True, e )
            # Check if THIS user has the required permissions
            cxxoneconn.checkpermissions( perm_cxone = True, perm_accesscontrol = False )      
            
            # Resolve project id
            pid = self.__resolve_project_id( cxxoneconn, projid, projname, scanid )
            if not pid :
                raise Exception( 'A matching project could not be found' )
            
            # Apply to project
            cxlogger.verbose( 'Updating project "' + str(pid) + '" with "' + reponame + '", branch "' + repobranch + '", token "*****"' )
            self.__update_project( cxxoneconn, pid, reponame, repobranch, repotoken )
            cxlogger.verbose( 'Project "' + str(pid) + '" updated' )
    
        except Exception as e:
            errorcount += 1
            cxlogger.verbose( str(e), True, False, True, e )
        
        if errorcount > 0 :
            sys.exit(9)
        else :
            sys.exit(0)
            
    
if __name__ == '__main__' :
    application = cxonereposet()
    application.execute()
    