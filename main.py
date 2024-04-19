from romaalbojob import RomaAlboJob 
from romatrasparentejob import RomaTrasparenteJob

#job = RomaAlboJob("1","COMUNE_DI_ROMA", "201", "ALBO_PRETORIO")
#job.run()
#job.report()

job = RomaTrasparenteJob("1","COMUNE_DI_ROMA", "1", "AMMINISTRAZIONE_TRASPARENTE")
job.run()
job.report()