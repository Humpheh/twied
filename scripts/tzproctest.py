import re

def proc_test(name):
    print ('b #', name, '#')

    if 'Pacific Time (US & Canada)' in name:
        print ('GO PST')
    if 'Eastern Time (US & Canada)' in name:
        print ('GO EST')
    if 'Central Time (US & Canada)' in name:
        print ('GO CST')

    name = re.sub(r'\([^)]*\)', '', name)
    name = name.strip()
    name = name.replace(' ', '_')
    print ('a #', name, '#')

proc_test('Indiana (East)')
proc_test('Pacific Time (US & Canada)')
proc_test('Eastern Time (US & Canada)')
proc_test('Central Time (US & Canada)')
proc_test('London')
