"""Real browser Python execution, error recovery, exports and responsive reading."""
import json, math, os, re, subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
LESSONS=json.loads((ROOT/'src/course.json').read_text())['lessons']
RESULTS=ROOT/'test-results'; RESULTS.mkdir(exist_ok=True)
BASE='http://127.0.0.1:5174/causal-inference-lab/'
def visit(page,path=''):
    page.goto(BASE+path)
    page.wait_for_selector('html[data-ready="true"]')
def wait_result(page):
    page.wait_for_function("/Completed|reported an error|could not finish/.test(document.querySelector('#status').textContent)",timeout=150000)
    assert page.locator('#status').inner_text().startswith('Completed'),page.locator('#output').inner_text()
def download(page,selector,name):
    with page.expect_download() as record:page.locator(selector).click()
    path=RESULTS/name;record.value.save_as(path);return path
server=subprocess.Popen([sys.executable,'-m','http.server','5174','--bind','127.0.0.1','--directory',str(ROOT/'.preview')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:urllib.request.urlopen(BASE,timeout=1);break
        except Exception:time.sleep(.1)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=None if os.environ.get('CI') else os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
        context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(('http://127.0.0.1:5174/','data:','blob:')) else route.abort())
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        visit(page)
        assert page.locator('.lesson-row').count()==18
        assert page.locator('h1').inner_text()=='What would happen if we changed it?'
        page.screenshot(path=str(RESULTS/'overview-desktop.png'),full_page=True)
        page.locator('#search').fill('collider')
        assert 0<page.locator('.lesson-row:visible').count()<18
        page.locator('#search').fill('unfindablezzzz')
        assert page.locator('#search-empty').is_visible()
        page.locator('#search').fill('')
        visit(page,'lessons/'+LESSONS[0]['slug']+'.html')
        assert not page.locator('#run-result').is_visible()
        assert not page.locator('#stop').is_visible()
        worked=json.loads((ROOT/'.cache/worked.json').read_text())['lessons']
        for i,l in enumerate(LESSONS):
            code=(ROOT/'python'/l['code']).read_text()
            page.locator('#code').fill(code);page.locator('#run').click();wait_result(page)
            actual=page.locator('#output').inner_text()
            expected=worked[l['slug']]['stdout']
            numbers=lambda s:[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',s)]
            a,b=numbers(actual),numbers(expected)
            assert len(a)==len(b),(l['slug'],actual,expected)
            assert all(math.isclose(x,y,rel_tol=2e-4,abs_tol=2e-4) for x,y in zip(a,b)),(l['slug'],actual,expected)
            assert page.locator('#plots img').count()==len(worked[l['slug']]['figures'])
            print('PASS browser Python:',l['slug'],flush=True)
        # Error, Stop and restart use actual runtime state, not mocked messages.
        page.locator('#code').fill("raise ValueError('deliberate test error')")
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('reported an error')")
        assert 'deliberate test error' in page.locator('#output').inner_text()
        page.locator('#code').fill('while True: pass')
        page.locator('#run').click();page.locator('#stop').click()
        assert 'Stopped' in page.locator('#status').inner_text()
        page.locator('#code').fill("print('recovered')")
        page.locator('#run').click();wait_result(page)
        assert 'recovered' in page.locator('#output').inner_text()
        # Draft restore and feedback on the actual lesson page.
        visit(page,'lessons/'+LESSONS[-1]['slug']+'.html')
        page.locator('#code').fill("print('exported exact source')")
        page.locator('#run').click();wait_result(page)
        code=page.locator('#code').input_value()
        page.locator('#report-question').fill('Does the specified course improve the 12-week score?')
        record=json.loads(download(page,'#export-run','run.json').read_text())
        assert record['course']=='causal-inference-lab' and record['source']==code
        assert record['versions']['pyodide']=='0.27.7'
        page.locator('#code').fill(code+'\n# edit after execution')
        assert 'changed' in page.locator('#output-provenance').inner_text()
        report=download(page,'#export-report','report.md').read_text()
        assert 'changed after this run' in report and 'exported exact source' in report
        page.locator(f'input[name=answer][value="{LESSONS[-1]["correct"]}"]').check()
        page.locator('#quiz button').click()
        assert 'That reasoning fits' in page.locator('#quiz-feedback').inner_text()
        page.locator('#mark-read').check()
        page.reload();page.wait_for_selector('html[data-ready="true"]')
        assert page.locator('#code').input_value().endswith('# edit after execution')
        assert page.locator('#report-question').input_value().startswith('Does the specified')
        assert page.locator('#mark-read').is_checked()
        page.locator('#editor-tools > summary').click();page.locator('#restore').click()
        assert page.locator('#code').input_value()==(ROOT/'python'/LESSONS[-1]['code']).read_text()
        page.screenshot(path=str(RESULTS/'lesson-desktop.png'),full_page=True)
        visit(page)
        assert page.locator('#progress-count').inner_text()=='1 / 18 read'
        page.locator('.portable-progress > summary').click()
        saved=download(page,'#export-progress','progress.json')
        data=json.loads(saved.read_text());assert data['course']=='causal-inference-lab'
        page.evaluate('localStorage.clear()');page.reload();page.wait_for_selector('html[data-ready="true"]')
        page.locator('.portable-progress > summary').click();page.locator('#import-progress').set_input_files(str(saved))
        page.wait_for_function("document.querySelector('#progress-status').textContent.startsWith('Imported')")
        assert page.locator('#progress-count').inner_text()=='1 / 18 read'
        # Phone layouts and each page's independently wired fresh question.
        page.set_viewport_size({'width':390,'height':844})
        for l in LESSONS:
            visit(page,'lessons/'+l['slug']+'.html')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),l['slug']
            page.locator(f'input[name=answer][value="{l["correct"]}"]').check()
            page.locator('#quiz button').click()
            assert 'That reasoning fits' in page.locator('#quiz-feedback').inner_text()
            page.locator('#course-menu-toggle').click()
            assert page.locator('#course-menu-toggle').get_attribute('aria-expanded')=='true'
            page.keyboard.press('Escape')
            assert page.locator('#course-menu-toggle').get_attribute('aria-expanded')=='false'
        page.screenshot(path=str(RESULTS/'lesson-mobile.png'),full_page=True)
        page.locator('#theme').click()
        assert page.evaluate('document.documentElement.dataset.theme')=='dark'
        page.screenshot(path=str(RESULTS/'lesson-dark.png'),full_page=True)
        nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        static=nojs.new_page();static.goto(BASE+'lessons/'+LESSONS[1]['slug']+'.html')
        assert static.locator('h1').inner_text()==LESSONS[1]['title']
        static.locator('.worked > summary').click()
        assert 'Observed difference: 15' in static.locator('.worked').inner_text()
        assert static.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors,errors
        browser.close()
        print('PASS: exports, drafts, feedback, Stop/restart, phone, theme and JavaScript-free reading.')
finally:
    server.terminate();server.wait()
