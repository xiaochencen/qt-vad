from classfication import thresholdFun as thd
from wavfeature import wavfeature as wf
import matplotlib.pyplot as plt
import until


wave = wf.Feature("E:\VsProject\speech\speech\D4_754.wav")
en = wave.st_en()
zcr = wave.st_zcr()
index_frame = thd.threshold(en, 1.2, 1.6)

#################################################
# Display #
'''
plt.subplot(211)
plt.plot(range(len(en)), en, 'b')
plt.subplot(212)
plt.plot(range(len(index_frame)), index_frame, 'g')
plt.show()
'''
#until.my_plot("test", x=(en, index_frame), y=(list(range(len(en))), list(range(len(index_frame)))))

##################################################
input("")

