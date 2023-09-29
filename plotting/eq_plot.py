from obspy import read

st = read('../DB/495323_sac/*TLN*',format='SAC')
st.detrend('linear')
st.taper(0.05,'hann')
st.filter('bandpass',freqmin=1.6,freqmax=42.5)
for tr in st:
	tr.data = tr.data*10**-9
st.plot(show=False,outfile='../Figures/TLN_wf.png',sharey=True)
