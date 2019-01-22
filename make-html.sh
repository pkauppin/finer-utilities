#!/bin/bash

#Linearizes input and outputs HTML, with matched entities highlighted and color-coded.
#The color codes are roughly as follows:
#- **blue**: locations (`EnamexLoc___`)
#- **red**: persons & beings (`EnamexPrs___`, excluding titles)
#- **green**: orgainzations (`EnamexOrg___`)
#- **purple**: products (`EnamexPro___`)
#- **dark gray: events (`EnamexEvt___`)
#- **light gray**: numerical expressions (`NumexMsr___`)
#- **yellow**: temporal expressions (`TimexTme___`)

echo "<html>
<head>
<style>
EnamexEvtXxx { background-color: #CCB ; }
EnamexLocXxx { background-color: #7CF ; }
EnamexLocAst { background-color: #0CD ; }
EnamexLocFnc { background-color: #0EF ; }
EnamexLocGpl { background-color: #AAF ; }
EnamexLocPpl { background-color: #7CF ; }
EnamexLocStr { background-color: #ADE ; }
EnamexOrgXxx { background-color: #5E5 ; }  
EnamexOrgAth { background-color: #7EB ; }
EnamexOrgClt { background-color: #0D9 ; }
EnamexOrgCrp { background-color: #5E5 ; }
EnamexOrgEdu { background-color: #0FC ; }
EnamexOrgFin { background-color: #AD6 ; }
EnamexOrgPlt { background-color: #BF0 ; }
EnamexOrgTvr { background-color: #9FA ; }
EnamexProXxx { background-color: #EAF ; }
EnamexPrsAnm { background-color: #EAA ; }
EnamexPrsHum { background-color: #F88 ; }
EnamexPrsMyt { background-color: #FA6 ; }
EnamexPrsTit { background-color: #EEE ; }
NumexMsrCur  { background-color: #EEE ; }
NumexMsrXxx  { background-color: #EEE ; }
TimexTmeDat  { background-color: #EE0 ; }
TimexTmeHrm  { background-color: #FD6 ; }
</style>
<body>
"

cat $STDIN | sed -r 's/^([^\t]+\t)([^\t]*\t\[[^\t]+\t[^\t]+\t)/\1/g' | cut -f 1,2 | ./linearize.sh

echo "

</body>
</html>"
