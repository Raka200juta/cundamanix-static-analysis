"""MobSF REST API V2 - Generate permission-only PDF Report."""
import logging
import os
import platform

from django.http import HttpResponse
from django.template.loader import get_template

from mobsf.MobSF import settings
from mobsf.MobSF.utils import is_md5
from mobsf.MobSF.views.api.api_middleware import make_api_response
from mobsf.StaticAnalyzer.models import (
    StaticAnalyzerAndroid,
    StaticAnalyzerIOS,
    RecentScansDB,
)
from mobsf.StaticAnalyzer.views.android.db_interaction import (
    get_context_from_db_entry as adb,
)
from mobsf.StaticAnalyzer.views.ios.db_interaction import (
    get_context_from_db_entry as idb,
)
from mobsf.StaticAnalyzer.views.common.appsec import (
    get_android_dashboard,
    get_ios_dashboard,
)

logger = logging.getLogger(__name__)


def pdf_report(request):
    """Generate and return a permission-only PDF for a given MD5 hash.

    Expects POST param 'hash'. Returns application/pdf on success.
    """
    try:
        checksum = request.POST.get('hash')
        if not checksum:
            return make_api_response({'error': 'Missing Parameters'}, 400)

        if not is_md5(checksum):
            return make_api_response({'error': 'Invalid Hash'}, 400)

        # Look up Android / iOS
        android_db = StaticAnalyzerAndroid.objects.filter(MD5=checksum)
        ios_db = StaticAnalyzerIOS.objects.filter(MD5=checksum)

        if android_db.exists():
            # get full context from DB (adb expects a QuerySet)
            context = adb(android_db)
            # compute appsec dashboard
            context['appsec'] = get_android_dashboard(context, from_ctx=True)
            template = get_template('pdf/android_report_permissions.html')
        elif ios_db.exists():
            context = idb(ios_db)
            context['appsec'] = get_ios_dashboard(context, from_ctx=True)
            template = get_template('pdf/ios_report_permissions.html')
        else:
            return make_api_response({'error': 'Report not found'}, 404)

        # add auxiliary context similar to common/pdf.py
        context['virus_total'] = None
        ext = os.path.splitext(context.get('file_name', '').lower())[1]
        # base paths for static assets
        proto = 'file://'
        host_os = 'nix'
        if platform.system() == 'Windows':
            proto = 'file:///'
            host_os = 'windows'
        context['base_url'] = proto + settings.BASE_DIR
        context['dwd_dir'] = proto + settings.DWD_DIR
        context['host_os'] = host_os
        try:
            context['timestamp'] = RecentScansDB.objects.get(MD5=checksum).TIMESTAMP
        except Exception:
            context['timestamp'] = ''

        # Render HTML and convert to PDF using pdfkit (similar to existing generator)
        try:
            try:
                import pdfkit
            except Exception:
                logger.exception('wkhtmltopdf/pdfkit not available')
                return make_api_response({'error': 'PDF generator not available'}, 500)

            options = {
                'page-size': 'Letter',
                'quiet': '',
                'enable-local-file-access': '',
                'no-collate': '',
                'margin-top': '0.50in',
                'margin-right': '0.50in',
                'margin-bottom': '0.50in',
                'margin-left': '0.50in',
                'encoding': 'UTF-8',
                'orientation': 'Landscape',
                'custom-header': [('Accept-Encoding', 'gzip')],
                'no-outline': None,
            }
            html = template.render(context)
            pdf_dat = pdfkit.from_string(html, False, options=options)
            return HttpResponse(pdf_dat, content_type='application/pdf')
        except Exception as exp:
            logger.exception('Error generating permission-only PDF')
            return make_api_response({'error': str(exp)}, 500)

    except Exception as exp:
        logger.exception('Error in permissions PDF endpoint')
        return make_api_response({'error': str(exp)}, 500)