def polish_sinhala(text):
    fixes = {
        "කල": "කළ",
        "ථහසෙන්": "මහසෙන්",
        "දහසේන": "ධාතුසේන",
        "කොමන්සු": "කරුණු",
        "අත්සන් කල": "සඳහන් කළ",
        "පිළිතුරු සඳහා": "පිළිතුරේ",
        "නිර්මාණ කිරීම හඳුනාගැනීම": "නිර්මාණ හඳුනාගෙන ඇත",
        "සහයෝගයෙන්": "අනුව"
    }

    for wrong, right in fixes.items():
        text = text.replace(wrong, right)

    return text