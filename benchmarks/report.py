"""Print Markdown tables from a completed benchmark report."""
import argparse
import json
from pathlib import Path


def tables(report):
    if not report['metadata'].get('finished_at_utc') or not report.get('summary'):
        raise ValueError('A completed benchmark report is required')
    for concurrency in report['metadata']['concurrency']:
        yield f'### Concurrency {concurrency}\n'
        yield '| Workload | Karak req/s (min–max) | FastAPI req/s (min–max) | Karak / FastAPI | Karak p95 / p99 ms | FastAPI p95 / p99 ms |'
        yield '| --- | ---: | ---: | ---: | ---: | ---: |'
        cases = dict.fromkeys(row['case'] for row in report['summary'])
        for case in cases:
            selected = {row['framework']: row for row in report['summary']
                        if row['case'] == case and row['concurrency'] == concurrency}
            karak = selected['karak']
            fastapi = selected['fastapi']
            def rate(row):
                return f"{row['median_rps']:,.0f} ({row['min_rps']:,.0f}–{row['max_rps']:,.0f})"
            yield (f"| {case} | {rate(karak)} | {rate(fastapi)} | "
                   f"{karak['median_rps'] / fastapi['median_rps']:.2f}× | "
                   f"{karak['median_p95_ms']:.1f} / {karak['median_p99_ms']:.1f} | "
                   f"{fastapi['median_p95_ms']:.1f} / {fastapi['median_p99_ms']:.1f} |")
        yield ''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print('\n'.join(tables(json.loads(args.report.read_text()))))


if __name__ == '__main__':
    main()
