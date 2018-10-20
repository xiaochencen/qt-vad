from classfication import thresholdFun as thd
from wavfeature import wavfeature as wf
import matplotlib.pyplot as plt
import numpy as np
import until


wave = wf.Feature("E:\VsProject\speech\speech\D4_754.wav")
en = wave.st_en()
zcr = wave.st_zcr()
feature = {'en': en, 'zcr': zcr}
index_frame = thd.threshold(feature)
test = dict()
test['y'] = np.ones(len(index_frame['y']))
print('%.2f' % until.calculate_accuracy(index_frame, test))
plt.plot(index_frame['y'])
plt.ylim(0,)
plt.xlim(min(index_frame['x']),)
plt.show()

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

