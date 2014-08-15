# coding: utf-8

import os
from lxml import etree

ANDROID_MANIFEST_XML = 'AndroidManifest.xml'
NAMESPACES           = {'android' : 'http://schemas.android.com/apk/res/android'}

class AndroidManifest(object):

    xpath_package_name       = '/manifest[@package]'
    xpath_version_code       = '/manifest[@android:versionCode]'
    xpath_version_name       = '/manifest[@android:versionName]'
    xpath_application        = '/manifest/application'

    _xpath_meta_data_node    = '/manifest/application/meta-data[@android:name="%s"]'
    xpath_db_version_code    = _xpath_meta_data_node % 'db_versionCode'
    xpath_channel            = _xpath_meta_data_node % 'channel'
    xpath_default_searchable = _xpath_meta_data_node % 'android.app.default_searchable'
    xpath_commit_id          = _xpath_meta_data_node % 'commit_id'

    attr_name_package     = 'package'
    attr_name_versionCode = 'android:versionCode'
    attr_name_versionName = 'android:versionName'
    attr_name_debuggable  = 'android:debuggable'
    attr_name_value       = 'android:value'

    def __init__(self, manifest=ANDROID_MANIFEST_XML):
        self.doc = etree.parse(manifest)
        self.def_package_name    = self._get(self.xpath_package_name, self.attr_name_package)
        self.def_version_code    = self._get(self.xpath_version_code, self.attr_name_versionCode)
        self.def_version_name    = self._get(self.xpath_version_name, self.attr_name_versionName)

        # Whether or not the application can be debugged, even when running on a device in user mode
        # — "true" if it can be, and "false" if not. The default value is "false".
        self.def_debuggable      = self._get(self.xpath_application, self.attr_name_debuggable)
        self.def_debuggable      = 'false' if self.def_debuggable is None else 'true'

        self.def_db_version_code = self._get(self.xpath_db_version_code, self.attr_name_value)
        self.def_channel         = self._get(self.xpath_channel, self.attr_name_value)
        self.def_searchable      = self._get(self.xpath_default_searchable, self.attr_name_value)
        self.commit_id           = self._get(self.xpath_commit_id, self.attr_name_value)

        self.dirty = False

    @staticmethod
    def _convert_attr_name(attr_name):
        if 'android:' in attr_name:
            return attr_name.replace('android:', '{%s}' % NAMESPACES['android'])
        else:
            return attr_name

    def _get(self, xpath, _attr_name):
        _attr_name = AndroidManifest._convert_attr_name(_attr_name)
        nodes = self.doc.xpath(xpath, namespaces=NAMESPACES)

        # assert len(nodes) == 1

        for node in nodes:
            for attr_name, attr_value in node.items():
                if attr_name == _attr_name:
                    return attr_value

    def set(self, xpath, _attr_name, _attr_value):
        _attr_name = self._convert_attr_name(_attr_name)
        nodes = self.doc.xpath(xpath, namespaces=NAMESPACES)
        for node in nodes:
            node.set(_attr_name, _attr_value)

            if not self.dirty:
                self.dirty = True

    def set_package_name(self, package_name):
        if package_name is not None and package_name != self.def_package_name:
            self.set(self.xpath_package_name, 'package', package_name)

            # res/xml directory
            scmd_email_np = "sed -i 's#xmlns:email=\"http://schemas.android.com/apk/res/%s\"#xmlns:email=\"http://schemas.android.com/apk/res/%s\"#' res/xml/%s"
            files = ['email_server_list.xml', 'services.xml']
            for file in files:
                os.system(scmd_email_np % (self.def_package_name, package_name, file))

            # res/drawable directory
            scmd_app_np = "sed -i 's#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#' res/drawable/%s"
            files = ['ic_folder_drafts.xml',    'ic_folder_inbox.xml',
                     'ic_folder_outbox.xml',    'ic_folder_sent.xml',
                     'ic_folder_star.xml',      'ic_folder_trash.xml',
                     'ic_folder_unkown.xml',    'ic_folder_unread.xml']
            for file in files:
                os.system(scmd_app_np % (self.def_package_name, package_name, file))

            # res/layout directory
            scmd_app_np = "sed -i 's#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#' res/layout/%s"
            files = ['cc_bcc_view.xml', 'compose_recipients.xml']
            for file in files:
                os.system(scmd_app_np % (self.def_package_name, package_name, file))

    def set_version_code(self, version_code):
        if version_code is not None and version_code != self.def_version_code:
            self.set(self.xpath_version_code, self.attr_name_versionCode, version_code)

    def set_version_name(self, version_name):
        if version_name is not None and version_name != self.def_version_name:
            self.set(self.xpath_version_name, self.attr_name_versionName, version_name)

    def set_debuggable(self, debuggable):
        if debuggable is not None and debuggable != self.def_debuggable:
            self.set(self.xpath_application, self.attr_name_debuggable, str(debuggable).lower())

    def set_db_version_code(self, db_version_code):
        if db_version_code is not None and db_version_code != self.def_db_version_code:
            import types
            if type(db_version_code) is types.IntType:
                db_version_code = str(db_version_code)
            self.set(self.xpath_db_version_code, self.attr_name_value, db_version_code)

    def set_channel(self, channel):
        if channel is not None and channel != self.def_channel:
            self.set(self.xpath_channel, self.attr_name_value, channel)

    def set_commit_id(self, commit_id):
        if commit_id is not None and commit_id != self.commit_id:
            self.set(self.xpath_commit_id, self.attr_name_value, commit_id)

    def set_searchable(self, searchable):
        if searchable is not None and searchable != self.def_searchable:
            self.set(self.xpath_default_searchable, self.attr_name_value, searchable)

    def tostring(self, format=None):
        if format is None:  format = '%-20s = %s'
        props = [format % ('package', self._get(self.xpath_package_name, self.attr_name_package)),
                 format % ('android:versionCode', self._get(self.xpath_version_code, self.attr_name_versionCode)),
                 format % ('android:versionName', self._get(self.xpath_version_name, self.attr_name_versionName)),
                 format % ('debuggable', 'false' if self._get(self.xpath_application, self.attr_name_debuggable) is None else 'true'),
                 format % ('db_versionCode', self._get(self.xpath_db_version_code, self.attr_name_value)),
                 format % ('channel', self._get(self.xpath_channel, self.attr_name_value)),
                 format % ('commit_id', self._get(self.xpath_commit_id, self.attr_name_value)),
                 format % ('def_searchable', self._get(self.xpath_default_searchable, self.attr_name_value))]
        return '\n'.join(props)

    def save(self):
        if self.dirty:
            self.doc.write(ANDROID_MANIFEST_XML, xml_declaration=True, encoding='utf-8')

    def __str__(self):
        return self.tostring()

#################################
# AndroidManifest default value #
#################################

__manifest      = AndroidManifest()

APK_CHANNEL     = __manifest.def_channel
DB_VERSION_CODE = __manifest.def_db_version_code
DEBUG           = True if __manifest.def_debuggable == 'true' else False
PACKAGE_NAME    = __manifest.def_package_name
SEARCHABLE      = __manifest.def_searchable
VERSION_CODE    = __manifest.def_version_code
VERSOIN_NAME    = __manifest.def_version_name
COMMIT_ID       = __manifest.commit_id

del __manifest

