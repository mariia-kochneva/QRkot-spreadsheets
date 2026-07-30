from datetime import datetime, timedelta
from io import BytesIO
from typing import Any

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient


def format_time_delta(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    if days:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    projects: list[dict[str, Any]],
    client: YandexDiskClient,
) -> str:
    report_date = datetime.now()
    filename = f'Отчет_{
        report_date.strftime(settings.report_format)
    }'.replace('/', '_')
    title = filename.replace('.xlsx', '')

    upload_url, file_path = await client.create_excel_file(
        title=title, folder='QRKot_Reports'
    )

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': "#f4bc5d",
        'font_color': 'white',
        'border': 1,
        'border_color': '#BDBDBD',
        'align': 'center',
        'font_size': 12,
        'font_name': 'Courier New',
    })
    cell_format = workbook.add_format({
        'border': 1,
        'border_color': '#BDBDBD',
        'font_color': '#424242',
        'align': 'left',
        'valign': 'vcenter',
        'font_size': 11,
        'bg_color': '#FFF3E0',
        'font_name': 'Courier New',
        'text_wrap': True,
    })
    total_format = workbook.add_format({
        'bold': True,
        'bg_color': "#ffdb8f",
        'font_color': 'white',
        'border': 1,
        'border_color': '#BDBDBD',
        'align': 'right',
        'font_size': 12,
        'font_name': 'Courier New',
    })

    worksheet.merge_range(
        0, 0, 0, 2,
        f'Отчёт от {report_date.strftime(settings.report_format)}',
        header_format,
    )

    columns = ['Название проекта', 'Время сбора', 'Описание']
    for col, value in enumerate(columns):
        worksheet.write(1, col, value, header_format)

    for row_idx, project in enumerate(projects, start=2):
        name = project.get('name', '')
        duration = project.get('duration', timedelta())
        description = project.get('description', '')

        worksheet.write(row_idx, 0, name, cell_format)
        worksheet.write(row_idx, 1, format_time_delta(duration), cell_format)
        worksheet.write(row_idx, 2, description, cell_format)

    total_row = len(projects) + 2
    worksheet.merge_range(
        total_row, 0, total_row, 2,
        f'Всего проектов: {len(projects)}',
        total_format,
    )

    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 1, 18)
    worksheet.set_column(2, 2, 50)

    workbook.close()
    output.seek(0)

    await client.upload_file(upload_url, output.getvalue())
    public_url = await client.publish_file(file_path)
    return public_url
