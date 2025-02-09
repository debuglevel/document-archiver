import datetime
import io
import pprint
import re
from dateutil.tz import tzutc, tzoffset
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_datetime(pdf_bytes: bytes) -> datetime:
    logger.debug("Getting datetime from PDF...")

    with io.BytesIO(pdf_bytes) as file:
        pdf_parser = PDFParser(file)
        pdf_document = PDFDocument(pdf_parser)

        creation_datetime_bytes = pdf_document.info[0]['CreationDate']  # b"D:20130501200439+01'00'"
        creation_datetime_string = creation_datetime_bytes.decode("utf-8")
        datetime1 = transform_datetime(creation_datetime_string)

        logger.debug(f"Got datetime from PDF: {pprint.pformat(datetime1)}")
        return datetime1


def transform_datetime(datetime_str: str) -> datetime:
    """
    Converts a pdf date such as "D:20120321183444+07'00'" into a usable datetime
    http://www.verypdf.com/pdfinfoeditor/pdf-date-format.htm
    (D:YYYYMMDDHHmmSSOHH'mm')
    :param datetime_str: pdf date string
    :return: datetime object
    """
    logger.debug(f"Transforming datetime {datetime_str}...")

    pdf_date_pattern = re.compile(''.join([
        r"(D:)?",
        r"(?P<year>\d\d\d\d)",
        r"(?P<month>\d\d)",
        r"(?P<day>\d\d)",
        r"(?P<hour>\d\d)",
        r"(?P<minute>\d\d)",
        r"(?P<second>\d\d)",
        r"(?P<tz_offset>[+-zZ])?",
        r"(?P<tz_hour>\d\d)?",
        r"'?(?P<tz_minute>\d\d)?'?"]))

    match = re.match(pdf_date_pattern, datetime_str)
    if match:
        date_info = match.groupdict()

        for k, v in date_info.items():  # transform values
            if v is None:
                pass
            elif k == 'tz_offset':
                date_info[k] = v.lower()  # so we can treat Z as z
            else:
                date_info[k] = int(v)

        if date_info['tz_offset'] in ('z', None):  # UTC
            date_info['tzinfo'] = tzutc()
        else:
            multiplier = 1 if date_info['tz_offset'] == '+' else -1
            date_info['tzinfo'] = tzoffset(None, multiplier*(3600 * date_info['tz_hour'] + 60 * date_info['tz_minute']))

        for k in ('tz_offset', 'tz_hour', 'tz_minute'):  # no longer needed
            del date_info[k]

        datetime_datetime = datetime.datetime(**date_info)

        logger.debug(f"Transformed datetime {datetime_str} to {datetime_datetime}.")
        return datetime_datetime
