import time

from zope.interface import implements
from zope.interface import Interface

from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from plone.app.caching.interfaces import IETagValue
from plone.app.caching.interfaces import IPloneCacheSettings

from plone.app.caching.operations.utils import getContext
from plone.app.caching.operations.utils import safeLastModified

from Products.CMFCore.utils import getToolByName

class UserID(object):
    """The ``userid`` etag component, returning the current user's id
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        context = getContext(self.published)
        portal_state = queryMultiAdapter((context, self.request), name=u'plone_portal_state')
        if portal_state is None:
            return None
        
        member = portal_state.member()
        if member is None:
            return None
        
        return member.getId()

class Roles(object):
    """The ``roles`` etag component, returning the current user's roles,
    separated by semicolons
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        context = getContext(self.published)
        portal_state = queryMultiAdapter((context, self.request), name=u'plone_portal_state')
        if portal_state is None:
            return None
        
        if portal_state.anonymous():
            return 'Anonymous'
        
        member = portal_state.member()
        if member is None:
            return None
        
        return ';'.join(sorted(member.getRolesInContext(context)))

class Language(object):
    """The ``language`` etag component, returning the value of the
    HTTP_ACCEPT_LANGUAGE request key.
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        return self.request.get('HTTP_ACCEPT_LANGUAGE', '')

class UserLanguage(object):
    """The ``userLanguage`` etag component, returning the user's preferred
    language
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        context = getContext(self.published)
        portal_state = queryMultiAdapter((context, self.request), name=u'plone_portal_state')
        if portal_state is None:
            return None
        
        return portal_state.language()

class GZip(object):
    """The ``gzip`` etag component, returning 1 or 0 depending on whether
    GZip compression is enabled
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        registry = queryUtility(IRegistry)
        if registry is not None:
            settings = registry.forInterface(IPloneCacheSettings, check=False)
            gzip_capable = self.request.get('HTTP_ACCEPT_ENCODING', '').find('gzip') != -1
            return str(int(settings.enableCompression and gzip_capable))
        return '0'

class LastModified(object):
    """The ``lastModified`` etag component, returning the last modification
    timestamp
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        lastModified = safeLastModified(self.published)
        if lastModified is None:
            return None
        return str(time.mktime(lastModified.timetuple()))

class CatalogCounter(object):
    """The ``catalogCounter`` etag component, returning a counter which is
    incremented each time the catalog is updated.
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        context = getContext(self.published)
        tools = queryMultiAdapter((context, self.request), name=u'plone_tools')
        if tools is None:
            return None
        
        return str(tools.catalog().getCounter())

class ObjectLocked(object):
    """The ``locked`` etag component, returning 1 or 0 depending on whether
    the object is locked.
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        context = getContext(self.published)
        context_state = queryMultiAdapter((context, self.request), name=u'plone_context_state')
        if context_state is None:
            return None        
        return str(int(context_state.is_locked()))

class Skin(object):
    """The ``skin`` etag component, returning the current skin name.
    """
    
    implements(IETagValue)
    adapts(Interface, Interface)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def __call__(self):
        context = getContext(self.published)
        
        portal_skins = getToolByName(context, 'portal_skins', None)
        if portal_skins is None:
            return None
        
        requestVariable = portal_skins.getRequestVarname()
        if requestVariable in self.request:
            return self.request[requestVariable]
        
        return portal_skins.getDefaultSkin()
