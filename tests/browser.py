"""Real browser Python execution, error recovery, exports and responsive reading."""
import json, math, os, re, subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
LESSONS=json.loads((ROOT/'src/course.json').read_text())['lessons']
RESULTS=ROOT/'test-results'; RESULTS.mkdir(exist_ok=True)
# The literal edits shown to learners, with a visible result from each edit.
EDITS = [
    ([('80, 88', '80, 98')], r'Individual model effects: \[8 6 4 2 0 8\].*Population ATE \(score points\): 4\.666'),
    ([('[0, 0, 0, 1, 0, 1, 1, 1]', '[0, 1, 0, 1, 0, 1, 0, 1]')], r'Observed difference: 0\.0.*Model ATE: 0\.0.*High-preparation counts \(untreated, treated\): 2 2'),
    ([('time_zero=None', "time_zero='eligibility date'")], r"Vague missing fields: \['follow_up'\].*Checked for values in time_zero and follow_up only"),
    ([('counts = np.array([[90, 10], [10, 90]])', 'counts = np.array([[50, 50], [50, 50]])')], r'Overall difference: 5\.0.*Within-preparation differences: \[5\. 5\.\].*standardised difference: 5\.0'),
    ([('admitted = (skill + luck) >= 1', 'admitted = (skill + luck) <= 1')], r'Population correlation: 0\.0.*Correlation after selecting admission: -0\.5'),
    ([('training_to_practice = 2', 'training_to_practice = 0')], r'Total model effect: 3.*Effect with practice held at zero: 3'),
    ([('[0.8, 0.2]', '[0.2, 0.8]')], r'Target average difference: 8\.4.*Equal-mix difference: 6\.0'),
    ([('treatment_effect = 5', 'treatment_effect = -3')], r'Observed difference: 15\.0.*Weighted difference: -3\.0'),
    ([('1., 100.', '1., 1.')], r'Records: 10 Weight-based effective sample size: 10\.0.*Groups with an empty treatment cell: \[1\]'),
    ([('[0, 1, 1, 1]', '[0, 0, 0, 1]'), ('[42., 80., 80., 80.]', '[42., 42., 42., 80.]')], r'ATT: 4\.0.*ATE in an equal-mix population: 6\.0'),
    ([('group_specific_trend = 0', 'group_specific_trend = 3')], r'Treated group change: 13.*Comparison group change: 6.*Difference-in-differences: 7.*Authored effect: 4'),
    ([('0.8 * score', '0 * score')], r'Window: 5\.0 Raw local difference: 5\.0.*Window: 1\.0 Raw local difference: 5\.0.*Window: 0\.2 Raw local difference: 5\.0.*True discontinuity at cutoff: 5'),
    ([('direct_invitation_effect = 0', 'direct_invitation_effect = 1')], r'Attendance change: 0\.333.*Invitation outcome change: 3\.0.*Wald ratio: 9\.0'),
    ([('n = 2000', 'n = 8000')], r'Unadjusted contrast: 1[34]\..*Approximate 95% bootstrap interval: \[1[34]\..*Authored causal effect: 2'),
    ([('prevalence_gap = 0.4', 'prevalence_gap = 0.2')], r'Hypothetical U effect: 15 Bias: 3\.0 Remaining contrast: 1\.0'),
    ([('[False, False, True, True]', '[True, True, True, True]')], r'Full model effect: 5\.0.*Available-case contrast: 5\.0.*Observed fractions: 1\.0 1\.0'),
    ([('destination_mix = np.array([0.2, 0.8])', 'destination_mix = np.array([0.5, 0.5])')], r'Study average effect: 6\.8.*Destination average under transport assumptions: 5\.0'),
    ([('[70., 75.]', '[70., 80.]')], r'Invented target proportions: \[0\.5 0\.5\].*Unadjusted contrast \(points\): 27\.0.*Standardised contrast \(points\): 7\.5'),
]
BASE='http://127.0.0.1:5174/causal-inference-lab/'
def visit(page,path=''):
    page.goto(BASE+path)
    page.wait_for_selector('html[data-ready="true"]')
def wait_result(page):
    page.wait_for_function("/Completed|reported an error|could not finish/.test(document.querySelector('#status').textContent)",timeout=150000)
    assert page.locator('#status').inner_text().startswith('Completed'),page.locator('#error-summary').text_content()
def download(page,selector,name):
    if selector=='#export-run' and not page.locator('.result-tools').evaluate('(details) => details.open'):
        page.locator('.result-tools > summary').click()
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
        editor=page.locator('#code')
        initial=editor.input_value()
        editor.press('Tab')
        assert page.locator('#run').evaluate("(button) => button === document.activeElement")
        assert editor.input_value()==initial
        worked=json.loads((ROOT/'.cache/worked.json').read_text())['lessons']
        for i,(l,(replacements,expected_edit)) in enumerate(zip(LESSONS,EDITS,strict=True)):
            visit(page,'lessons/'+l['slug']+'.html')
            code=(ROOT/'python'/l['code']).read_text()
            assert page.locator('#code').input_value()==code
            page.locator('#run').click();wait_result(page)
            actual=page.locator('#output').inner_text()
            expected=worked[l['slug']]['stdout']
            numbers=lambda s:[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',s)]
            a,b=numbers(actual),numbers(expected)
            assert len(a)==len(b),(l['slug'],actual,expected)
            assert all(math.isclose(x,y,rel_tol=2e-4,abs_tol=2e-4) for x,y in zip(a,b)),(l['slug'],actual,expected)
            assert page.locator('#plots img').count()==len(worked[l['slug']]['figures'])
            assert page.locator('#example-takeaway').is_visible(),l['slug']
            assert 'published code' in page.locator('#output-provenance').inner_text()
            assert not page.locator('.result-tools').evaluate('(details) => details.open')
            edited=code
            for old,new in replacements:
                assert edited.count(old)==1,(l['slug'],old)
                edited=edited.replace(old,new)
            page.locator('.change-task a').press('Enter')
            assert page.locator('#code').evaluate('(editor) => editor === document.activeElement')
            page.locator('#code').fill(edited)
            page.locator('#code').press('Control+Enter')
            wait_result(page)
            edited_output=page.locator('#output').inner_text()
            assert re.search(expected_edit,edited_output,re.S),(l['slug'],edited_output)
            if l['slug']=='uncertainty-is-not-identification':
                endpoints=lambda output:[float(x) for x in re.search(r'interval: \[([^]]+)\]',output)[1].split()]
                lo,hi=endpoints(actual)
                edit_lo,edit_hi=endpoints(edited_output)
                assert edit_hi-edit_lo < hi-lo and edit_lo>2
            assert not page.locator('#example-takeaway').is_visible()
            assert not page.locator('#run-error').is_visible()
            assert 'edited code' in page.locator('#output-provenance').inner_text()
            print('PASS browser Python and documented edit:',l['slug'],flush=True)
        # Error, Stop and restart use actual runtime state, not mocked messages.
        previous_output=page.locator('#output').inner_text()
        page.locator('#code').fill("raise ValueError('deliberate test error')")
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('reported an error')")
        assert 'deliberate test error' in page.locator('#error-summary').inner_text()
        assert page.locator('#output').inner_text()==previous_output
        page.locator('#code').fill('while True: pass')
        page.locator('#run').press('Enter')
        assert page.locator('#stop').evaluate("(button) => button === document.activeElement")
        page.locator('#stop').press('Enter')
        assert 'Stopped' in page.locator('#status').inner_text()
        assert page.locator('#run').evaluate("(button) => button === document.activeElement")
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
        edited_code="raise ValueError('a later failed attempt')"
        page.locator('#code').fill(edited_code)
        assert 'differs' in page.locator('#output-provenance').inner_text()
        page.locator('#run').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('reported an error')")
        assert 'a later failed attempt' in page.locator('#error-summary').inner_text()
        record_after_error=json.loads(download(page,'#export-run','run-after-error.json').read_text())
        assert record_after_error==record
        report=download(page,'#export-report','report.md').read_text()
        assert 'changed after this run' in report and 'exported exact source' in report
        assert 'a later failed attempt' not in report
        page.locator(f'input[name=answer][value="{LESSONS[-1]["correct"]}"]').check()
        page.locator('#quiz button').click()
        assert 'That reasoning fits' in page.locator('#quiz-feedback').inner_text()
        page.locator('#mark-read').check()
        page.reload();page.wait_for_selector('html[data-ready="true"]')
        assert page.locator('#code').input_value()==edited_code
        assert page.locator('#saved-draft').is_visible()
        assert page.locator('#report-question').input_value().startswith('Does the specified')
        assert page.locator('#mark-read').is_checked()
        page.locator('#editor-tools > summary').click();page.locator('#restore').click()
        assert page.locator('#code').input_value()==(ROOT/'python'/LESSONS[-1]['code']).read_text()
        page.reload();page.wait_for_selector('html[data-ready="true"]')
        page.locator('#editor-tools > summary').click();page.locator('#recover-draft').click()
        assert page.locator('#code').input_value()==edited_code
        assert page.locator('#code').evaluate("(editor) => editor === document.activeElement")
        page.screenshot(path=str(RESULTS/'lesson-desktop.png'),full_page=True)
        visit(page)
        assert page.locator('#progress-count').inner_text()=='1 / 18 read'
        page.locator('.portable-progress > summary').click()
        saved=download(page,'#export-progress','progress.json')
        data=json.loads(saved.read_text());assert data['course']=='causal-inference-lab'
        assert data['data']['draft:'+LESSONS[-1]['slug']+':restore-backup']==edited_code
        page.evaluate('localStorage.clear()');page.reload();page.wait_for_selector('html[data-ready="true"]')
        page.locator('.portable-progress > summary').click();page.locator('#import-progress').set_input_files(str(saved))
        page.wait_for_function("document.querySelector('#progress-status').textContent.startsWith('Imported')")
        assert page.locator('#progress-count').inner_text()=='1 / 18 read'
        # Phone layouts and each page's independently wired fresh question.
        page.set_viewport_size({'width':390,'height':844})
        page.locator('#theme').press('Enter')
        for l in LESSONS:
            visit(page,'lessons/'+l['slug']+'.html')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),l['slug']
            assert page.evaluate('document.documentElement.dataset.theme')=='dark'
            assert page.locator('.observation').is_visible()
            assert page.locator('.change-task').is_visible()
            assert not page.locator('#lesson-hints details').count()
            assert not page.locator('#lesson-hints li').first.is_visible()
            page.locator('#lesson-hints > summary').press('Enter')
            assert page.locator('#lesson-hints li').first.is_visible()
            wrong=(l['correct']+1)%len(l['options'])
            page.locator(f'input[name=answer][value="{wrong}"]').check()
            page.locator('#quiz button').press('Enter')
            assert 'Reconsider the comparison' in page.locator('#quiz-feedback').inner_text()
            page.locator(f'input[name=answer][value="{l["correct"]}"]').check()
            assert page.locator('#quiz-feedback').inner_text()==''
            page.locator('#quiz button').click()
            assert 'That reasoning fits' in page.locator('#quiz-feedback').inner_text()
            page.locator('#course-menu-toggle').click()
            assert page.locator('#course-menu-toggle').get_attribute('aria-expanded')=='true'
            page.keyboard.press('Escape')
            assert page.locator('#course-menu-toggle').get_attribute('aria-expanded')=='false'
        page.screenshot(path=str(RESULTS/'lesson-mobile.png'),full_page=True)
        page.screenshot(path=str(RESULTS/'lesson-dark.png'),full_page=True)
        page.locator('#theme').press('Enter')
        assert page.evaluate('document.documentElement.dataset.theme')=='light'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')

        # A denied storage getter must not claim that a draft was saved or that
        # an empty progress file contains the learner's records.
        denied=browser.new_context(accept_downloads=True,viewport={'width':390,'height':844})
        denied.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError')}});")
        blocked=denied.new_page()
        visit(blocked,'lessons/'+LESSONS[0]['slug']+'.html')
        blocked.locator('#lesson-notes > summary').press('Enter')
        assert not blocked.locator('#save-note').is_visible()
        blocked.locator('#notes').fill('These are new notes.')
        assert 'on this page only' in blocked.locator('#save-note').inner_text()
        assert blocked.locator('#storage-error').is_visible()
        blocked.locator('#mark-read').press('Space')
        assert not blocked.locator('#mark-read').is_checked()
        assert 'could not save the reading mark' in blocked.locator('#read-status').inner_text()
        assert 'latest changes' in blocked.locator('#storage-error').inner_text()
        visit(blocked)
        blocked.locator('.portable-progress > summary').press('Enter')
        blocked.locator('#export-progress').press('Enter')
        assert 'Progress was not exported' in blocked.locator('#progress-status').inner_text()
        denied.close()
        nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        static=nojs.new_page();static.goto(BASE+'lessons/'+LESSONS[1]['slug']+'.html')
        assert static.locator('h1').inner_text()==LESSONS[1]['title']
        assert not static.locator('#run').is_visible()
        assert static.locator('#code').get_attribute('readonly') is not None
        fallback=static.locator('#practice noscript p')
        assert fallback.is_visible() and fallback.inner_text()=='Enable JavaScript to check your answer.'
        static.locator('.worked > summary').click()
        assert 'Observed difference: 15' in static.locator('.worked').inner_text()
        assert static.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors,errors
        browser.close()
        print('PASS: exports, drafts, feedback, Stop/restart, phone, theme and JavaScript-free reading.')
finally:
    server.terminate();server.wait()
