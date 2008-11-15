
all:translations/boincgui_sk.qm BoincGui/resources.py

clean:
	rm -f translations/boincgui_sk.qm
	rm -f BoincGui/resources.py
	rm -f *~
	rm -f *.pyc
	rm -f Boinc/*~
	rm -f Boinc/*.pyc
	rm -f BoincGui/*~
	rm -f BoincGui/*.pyc

translations/boincgui_sk.qm:translations/boincgui_sk.ts
	lrelease $< $@

translations/boincgui_sk.ts:
	pylupdate4 -noobsolete pyboincgui.pro

BoincGui/resources.py:BoincGui/resources.qrc
	pyrcc4 $< > $@

.PHONY: all clean translations/boincgui_sk.ts
