import logging
from pathlib import Path
import os

import lief

from django.conf import settings

from mobsf.MobSF.utils import (
    append_scan_status,
    settings_enabled,
)
from mobsf.StaticAnalyzer.views.common.binary.elf import (
    ELFChecksec,
)
from mobsf.StaticAnalyzer.views.common.binary.macho import (
    MachOChecksec,
)


logger = logging.getLogger(__name__)


def library_analysis(checksum, src, arch):
    """Perform library binary analysis."""
    base_dir = Path(settings.UPLD_DIR) / checksum
    res = {
        f'{arch}_analysis': [],
        f'{arch}_strings': [],
        f'{arch}_symbols': [],
        'framework_analysis': [],
        'framework_strings': [],
        'framework_symbols': [],
    }
    try:
        if arch == 'macho':
            analysis = MachOChecksec
            ext = '*.dylib'
            if not settings_enabled('DYLIB_ANALYSIS_ENABLED'):
                return res
        elif arch == 'elf':
            analysis = ELFChecksec
            ext = '*.so'
            if not settings_enabled('SO_ANALYSIS_ENABLED'):
                return res
        elif arch == 'ar':
            ext = '*.o'
            res[f'{arch}_a'] = ''

        msg = 'Library Binary Analysis Started'
        logger.info(msg)
        append_scan_status(checksum, msg)

        # Supports Static Library, Shared objects, Dynamic Library,
        # from APK, SO, AAR, JAR, IPA, DYLIB, and A
        for libfile in Path(src).rglob(ext):
            if '__MACOSX' in libfile.as_posix():
                continue
            rel_path = libfile.relative_to(base_dir).as_posix()
            msg = f'Analyzing {rel_path}'
            logger.info(msg)
            append_scan_status(checksum, msg)

            if arch == 'ar':
                # Handle static library
                if lief.is_macho(libfile.as_posix()):
                    analysis = MachOChecksec
                    res[f'{arch}_a'] = 'MachO'
                elif lief.is_elf(libfile.as_posix()):
                    analysis = ELFChecksec
                    res[f'{arch}_a'] = 'ELF'
                else:
                    continue

            chk = analysis(libfile, rel_path)
            chksec = chk.checksec()
            strings = chk.strings()
            symbols = chk.get_symbols()

            if chksec:
                res[f'{arch}_analysis'].append(chksec)
            if strings:
                res[f'{arch}_strings'].append({
                    rel_path: strings})
            if symbols:
                res[f'{arch}_symbols'].append({
                    rel_path: symbols})
        if ext == '*.dylib':
            frameworks_analysis(checksum, src, base_dir, res)
            if res['framework_strings']:
                res[f'{arch}_strings'].extend(
                    res['framework_strings'])
    except Exception as exp:
        msg = 'Error Performing Library Binary Analysis'
        logger.exception(msg)
        append_scan_status(checksum, msg, repr(exp))
    return res


def frameworks_analysis(checksum, src, base_dir, res):
    """Binary Analysis on Frameworks."""
    try:
        msg = 'Framework Binary Analysis Started'
        logger.info(msg)
        append_scan_status(checksum, msg)
        # Supports iOS Frameworks
        for ffile in Path(src).rglob('*'):
            parent_name = ffile.parents[0].name
            if not parent_name.lower().endswith('.framework'):
                continue
            if ffile.suffix != '':
                continue
            if ffile.name.lower() not in parent_name.lower():
                continue
            rel_path = _safe_relpath(ffile, base_dir)
            msg = f'Analyzing {rel_path}'
            logger.info(msg)
            append_scan_status(checksum, msg)
            chk = MachOChecksec(ffile, rel_path)
            chksec = chk.checksec()
            strings = chk.strings()
            symbols = chk.get_symbols()
            if chksec:
                res['framework_analysis'].append(chksec)
            if strings:
                res['framework_strings'].append({
                    rel_path: strings})
            if symbols:
                res['framework_symbols'].append({
                    rel_path: symbols})
    except Exception as exp:
        msg = 'Error Performing Framework Binary Analysis'
        logger.exception(msg)
        append_scan_status(checksum, msg, repr(exp))

def _safe_relpath(path_obj: Path, base_dir: Path) -> str:
    """Compute relpath  roustly even if ase_dir not a strict parent (cross-OS)."""
    try:
        return path_obj.relative_to(base_dir).as_posix()
    except Exception:
        return os.path.relpath(path_obj.as_posix(), base_dir.as_posix())