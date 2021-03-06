from __future__ import division
from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *
from heppy.particles.tlv.resonance import Resonance2 as Resonance
from heppy.particles.tlv.particle import Particle

import math
import ROOT
from ROOT import *
import collections
from array import array

#For TMVA >>>>>>>>>>>>>>>>>>>>>
#ROOT.gROOT.ProcessLine('.L /afs/cern.ch/user/r/rasmith/fcc/heppy/FCChhAnalyses/Zprime_tt/BDT_QCD.class.C+')

class TreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        
        self.tree.var('weight', float)
        self.tree.var('missingET', float)
        self.tree.var('numberOfElectrons', int)
        self.tree.var('numberOfMuons', int)

        #trk02 no SD
        self.tree.var('Jet1_trk02_tau1', float)       
        self.tree.var('Jet1_trk02_tau2', float)
        self.tree.var('Jet1_trk02_tau3', float)
        self.tree.var('Jet2_trk02_tau1', float)
        self.tree.var('Jet2_trk02_tau2', float)
        self.tree.var('Jet2_trk02_tau3', float)
        self.tree.var('Jet1_trk02_tau32', float)
        self.tree.var('Jet1_trk02_tau31', float)
        self.tree.var('Jet1_trk02_tau21', float)
        self.tree.var('Jet2_trk02_tau32', float)
        self.tree.var('Jet2_trk02_tau31', float)
        self.tree.var('Jet2_trk02_tau21', float)
 
        #bookParticle(self.tree, 'Jet1_trk02_Corr')
        #bookParticle(self.tree, 'Jet2_trk02_Corr')

        #bookParticle(self.tree, 'Jet1_trk02_MetCorr')
        #bookParticle(self.tree, 'Jet2_trk02_MetCorr')

        bookParticle(self.tree, 'Jet1_trk02_Corr_MetCorr')
        bookParticle(self.tree, 'Jet2_trk02_Corr_MetCorr')

        self.tree.var('rapiditySeparation_trk02', float)
        self.tree.var('transverseMomentumAsymmetry_trk02', float)
        self.tree.var('topJetMassDifference', float)


        #trk02 SD
        #bookParticle(self.tree, 'Jet1_trk02_SD')
        #bookParticle(self.tree, 'Jet2_trk02_SD')

        bookParticle(self.tree, 'Jet1_trk02_SD_Corr')
        bookParticle(self.tree, 'Jet2_trk02_SD_Corr')

        bookParticle(self.tree, 'Jet1_trk02_SD_MetCorr')
        bookParticle(self.tree, 'Jet2_trk02_SD_MetCorr')
        
        bookParticle(self.tree, 'Jet1_trk02_SD_Corr_MetCorr')
        bookParticle(self.tree, 'Jet2_trk02_SD_Corr_MetCorr')
 
        bookParticle(self.tree, 'Electron1')
        bookParticle(self.tree, 'Electron2')

        bookParticle(self.tree, 'Muon1')
        bookParticle(self.tree, 'Muon2')

        #self.tree.var('BDTvariable_qcd', float)

        self.tree.var('Mj1j2_trk02', float)
        self.tree.var('Mj1j2_trk02_Corr', float)
        self.tree.var('Mj1j2_trk02_MetCorr', float)
        self.tree.var('Mj1j2_trk02_Corr_MetCorr', float)

        self.tree.var('Mj1j2_pf02', float)
        self.tree.var('Mj1j2_pf02_MetCorr', float)

        self.tree.var('Mj1j2_pf04', float)
        self.tree.var('Mj1j2_pf04_MetCorr', float)

        self.tree.var('Mj1j2_pf08', float)
        self.tree.var('Mj1j2_pf08_MetCorr', float)

        self.tree.var('Jet1_trk02_dR_lep', float)
        self.tree.var('Jet2_trk02_dR_lep', float)


    def corrMET(self, jet1, pdg1 , jet2, pdg2, met):
        dphi1 = abs(jet1.p4().DeltaPhi(met.p4()))
        dphi2 = abs(jet2.p4().DeltaPhi(met.p4()))

        metp4 = ROOT.TLorentzVector()
        px = met.p4().Px()
        py = met.p4().Py()
            
        if (dphi1 < dphi2):
            pz = jet1.p4().Pz()/2.
            e = math.sqrt(px**2 + py**2 + pz**2)
            metp4.SetPxPyPzE(px, py, pz, e) 
            jetcorr1   = Particle(pdg1, 0, jet1.p4() + metp4, 1)
            jetcorr2   = Particle(pdg2, 0, jet2.p4(), 1)
        else:
            pz = jet2.p4().Pz()/2.
            e = math.sqrt(px**2 + py**2 + pz**2)
            metp4.SetPxPyPzE(px, py, pz, e) 
            jetcorr1  = Particle(pdg1, 0, jet1.p4(), 1)
            jetcorr2  = Particle(pdg2, 0, jet2.p4() + metp4, 1)
        return jetcorr1,jetcorr2

    def fillMass(self, jet1, jet2):
        mj1j2 = ROOT.TLorentzVector()
        j1 = ROOT.TLorentzVector(); j2 = ROOT.TLorentzVector()
        j1.SetPtEtaPhiE(jet1.pt(), jet1.eta(), jet1.phi(), jet1.e())
        j2.SetPtEtaPhiE(jet2.pt(), jet2.eta(), jet2.phi(), jet2.e())
        mj1j2 = j1+j2
        return mj1j2.M()

     
    def process(self, event):
        self.tree.reset()
        jets_trk02 = getattr(event, self.cfg_ana.jets_trk02_1000)
        jets_pf02 = getattr(event, self.cfg_ana.jets_pf02_1500)
        jets_pf04 = getattr(event, self.cfg_ana.jets_pf04_1000)
        jets_pf08 = getattr(event, self.cfg_ana.jets_pf08_1500)

        
        electrons = getattr(event, self.cfg_ana.electrons)
        muons = getattr(event, self.cfg_ana.muons)

        Jet1_trk02_dR_lep = 999
        Jet2_trk02_dR_lep  = 999
        if ( len(jets_trk02)>=2 and  len(jets_pf02)>=2):

            j1 = ROOT.TLorentzVector(); j2 = ROOT.TLorentzVector()
            j1.SetPtEtaPhiE(jets_trk02[0].pt(), jets_trk02[0].eta(), jets_trk02[0].phi(), jets_trk02[0].e())
            j2.SetPtEtaPhiE(jets_trk02[1].pt(), jets_trk02[1].eta(), jets_trk02[1].phi(), jets_trk02[1].e())
            if ( len(electrons)!=0 and len(muons)==0 ):
                e = ROOT.TLorentzVector()
                e.SetPtEtaPhiE(electrons[0].pt(), electrons[0].eta(), electrons[0].phi(), electrons[0].e())
                Jet1_dR = j1.DeltaR(e)
                Jet2_dR = j2.DeltaR(e)
            if ( len(electrons)==0 and len(muons)!=0 ):
                m = ROOT.TLorentzVector()
                m.SetPtEtaPhiE(muons[0].pt(), muons[0].eta(), muons[0].phi(), muons[0].e())
                Jet1_dR = j1.DeltaR(m)
                Jet2_dR = j2.DeltaR(m)
            if ( len(electrons)!=0 and len(muons)!=0 ):
                isElectron = False; isMuon = False
                if ( electrons[0].pt() > muons[0].pt() ): isElectron = True
                else: isMuon = True
                l = ROOT.TLorentzVector()
                if isElectron: l.SetPtEtaPhiE(electrons[0].pt(), electrons[0].eta(), electrons[0].phi(), electrons[0].e())
                if isMuon: l.SetPtEtaPhiE(muons[0].pt(), muons[0].eta(), muons[0].phi(), muons[0].e())
                Jet1_trk02_dR_lep  = j1.DeltaR(l)
                Jet2_trk02_dR_lep  = j2.DeltaR(l)
            
            self.tree.fill('Jet1_trk02_dR_lep' , Jet1_trk02_dR_lep )
            self.tree.fill('Jet2_trk02_dR_lep' , Jet2_trk02_dR_lep )

            self.tree.fill('weight' , event.weight )
            self.tree.fill('missingET', event.met.pt())
            self.tree.fill('numberOfElectrons', len(electrons))
            self.tree.fill('numberOfMuons', len(muons))

            self.tree.fill('rapiditySeparation_trk02', abs(jets_trk02[0].eta() - jets_trk02[1].eta()))
            self.tree.fill('transverseMomentumAsymmetry_trk02', (jets_trk02[0].pt() - jets_trk02[1].pt())/(jets_trk02[0].pt() + jets_trk02[1].pt()))

            self.tree.fill('Jet1_trk02_tau1' , jets_trk02[0].tau1 )
            self.tree.fill('Jet1_trk02_tau2' , jets_trk02[0].tau2 )
            self.tree.fill('Jet1_trk02_tau3' , jets_trk02[0].tau3 )
            self.tree.fill('Jet2_trk02_tau1' , jets_trk02[1].tau1 )
            self.tree.fill('Jet2_trk02_tau2' , jets_trk02[1].tau2 )
            self.tree.fill('Jet2_trk02_tau3' , jets_trk02[1].tau3 )

            Jet1_trk02_tau31 = -999.0
            Jet1_trk02_tau21 = -999.0
            Jet1_trk02_tau32 = -999.0
            Jet2_trk02_tau31 = -999.0
            Jet2_trk02_tau21 = -999.0
            Jet2_trk02_tau32 = -999.0

            if (jets_trk02[0].tau1 != 0.0):
                Jet1_trk02_tau31 = jets_trk02[0].tau3/jets_trk02[0].tau1
                Jet1_trk02_tau21 = jets_trk02[0].tau2/jets_trk02[0].tau1 
            if (jets_trk02[0].tau2 != 0.0):
                Jet1_trk02_tau32 = jets_trk02[0].tau3/jets_trk02[0].tau2

            if (jets_trk02[1].tau1 != 0.0):
                Jet2_trk02_tau31 = jets_trk02[1].tau3/jets_trk02[1].tau1
                Jet2_trk02_tau21 = jets_trk02[1].tau2/jets_trk02[1].tau1
            if (jets_trk02[1].tau2 != 0.0):
                Jet2_trk02_tau32 = jets_trk02[1].tau3/jets_trk02[1].tau2

            self.tree.fill('Jet1_trk02_tau31', Jet1_trk02_tau31)
            self.tree.fill('Jet1_trk02_tau21', Jet1_trk02_tau21)
            self.tree.fill('Jet1_trk02_tau32', Jet1_trk02_tau32)
            self.tree.fill('Jet2_trk02_tau31', Jet2_trk02_tau31)
            self.tree.fill('Jet2_trk02_tau21', Jet2_trk02_tau21)
            self.tree.fill('Jet2_trk02_tau32', Jet2_trk02_tau32)

	    # here is btag, need matching in DR
            Jet1_trk02_dR_pf04 = 999
            Jet2_trk02_dR_pf04 = 999
	    for j in jets_pf04:
                pf04= ROOT.TLorentzVector()
                pf04.SetPtEtaPhiE(j.pt(), j.eta(), j.phi(), j.e())
                if j.tags['bf'] > 0:
                    if pf04.DeltaR(j1)<Jet1_trk02_dR_pf04:
                        Jet1_trk02_dR_pf04=pf04.DeltaR(j1)
                    if pf04.DeltaR(j2)<Jet2_trk02_dR_pf04:
                        Jet2_trk02_dR_pf04=pf04.DeltaR(j2)
            #print 'dr j1  ',Jet1_trk02_dR_pf04
            #print 'dr j2  ',Jet2_trk02_dR_pf04
            
            pdg1 = 0
            pdg2 = 0
            if Jet1_trk02_dR_pf04 < 0.3:
                pdg1 = 5
            if Jet2_trk02_dR_pf04 < 0.3:
                pdg2 = 5



            #MATCHING PF02 and trk02 for CORRECTION
            Jet1_trk02_dR_pf02 = 999
            Jet2_trk02_dR_pf02 = 999
            Jet1_pf02 = None
            Jet2_pf02 = None
            for j in jets_pf02:
                pf02= ROOT.TLorentzVector()
                pf02.SetPtEtaPhiE(j.pt(), j.eta(), j.phi(), j.e())
                if pf02.DeltaR(j1)<Jet1_trk02_dR_pf02:
                    Jet1_trk02_dR_pf02=pf02.DeltaR(j1)
                    Jet1_pf02=j
                if pf02.DeltaR(j2)<Jet2_trk02_dR_pf02:
                    Jet2_trk02_dR_pf02=pf02.DeltaR(j2)
                    Jet2_pf02=j
            #print 'jet1 dr ',Jet1_trk02_dR_pf02,'  pf02   ',Jet1_pf02,'  trk02  ',jets_trk02[0]
            #print 'jet2 dr ',Jet2_trk02_dR_pf02,'  pf02   ',Jet2_pf02,'  trk02  ',jets_trk02[1]

	    corr1 = Jet1_pf02.p4().Pt()/j1.Pt()
	    corr2 = Jet2_pf02.p4().Pt()/j2.Pt()

            #print 'corr 1  ',corr1,'   corr2  ',corr2
            #NORMAL TRK02 SD corrected jet
	    p4sd1 = ROOT.TLorentzVector(); p4sd2 = ROOT.TLorentzVector()
	    p4sd1.SetPtEtaPhiM(jets_trk02[0].subjetsSoftDrop[0].p4().Pt()*corr1, 
	    			jets_trk02[0].eta(), 
				jets_trk02[0].phi(), 
				jets_trk02[0].subjetsSoftDrop[0].p4().M()*corr1)
	    
	    p4sd2.SetPtEtaPhiM(jets_trk02[1].subjetsSoftDrop[0].p4().Pt()*corr2, 
	    			jets_trk02[1].eta(), 
				jets_trk02[1].phi(), 
				jets_trk02[1].subjetsSoftDrop[0].p4().M()*corr2)
	    
            sdjet1_corr = Particle(pdg1, 0, p4sd1, 1)
            sdjet2_corr = Particle(pdg2, 0, p4sd2, 1)
            fillParticle(self.tree, 'Jet1_trk02_SD_Corr', sdjet1_corr)
            fillParticle(self.tree, 'Jet2_trk02_SD_Corr', sdjet2_corr)

            #NORMAL TRK02 SD jet
	    #sdjet1 = Particle(pdg1, 0, jets_trk02[0].subjetsSoftDrop[0].p4(), 1)
            #sdjet2 = Particle(pdg2, 0, jets_trk02[1].subjetsSoftDrop[0].p4(), 1)
            #fillParticle(self.tree, 'Jet1_trk02_SD', sdjet1)
            #fillParticle(self.tree, 'Jet2_trk02_SD', sdjet2)

            #CORRECTED TRK02 jet
	    p4jet1_corr = ROOT.TLorentzVector(); p4jet2_corr = ROOT.TLorentzVector()
            p4jet1_corr.SetPtEtaPhiM(jets_trk02[0].pt()*corr1, jets_trk02[0].eta(), jets_trk02[0].phi(), jets_trk02[0].m()*corr1)
	    p4jet2_corr.SetPtEtaPhiM(jets_trk02[1].pt()*corr2, jets_trk02[1].eta(), jets_trk02[1].phi(), jets_trk02[1].m()*corr2)

            jet1_corr = Particle(pdg1, 0, p4jet1_corr, 1)
            jet2_corr = Particle(pdg2, 0, p4jet2_corr, 1)
            #fillParticle(self.tree, 'Jet1_trk02_Corr', jet1_corr)
            #fillParticle(self.tree, 'Jet2_trk02_Corr', jet2_corr)

 
            # associate MET to one jet or another based on softdrop
            sdjetmet1, sdjetmet2 = self.corrMET(jets_trk02[0].subjetsSoftDrop[0], pdg1, jets_trk02[1].subjetsSoftDrop[0], pdg2, event.met)
            fillParticle(self.tree, 'Jet1_trk02_SD_MetCorr', sdjetmet1)
            fillParticle(self.tree, 'Jet2_trk02_SD_MetCorr', sdjetmet2)

            sdjetmet1, sdjetmet2 = self.corrMET(sdjet1_corr, pdg1, sdjet2_corr, pdg2, event.met)
            fillParticle(self.tree, 'Jet1_trk02_SD_Corr_MetCorr', sdjetmet1)
            fillParticle(self.tree, 'Jet2_trk02_SD_Corr_MetCorr', sdjetmet2)



            if (len(jets_trk02)>1): 
                self.tree.fill( 'Mj1j2_trk02',self.fillMass(jets_trk02[0],jets_trk02[1]))
                self.tree.fill( 'Mj1j2_trk02_Corr',self.fillMass(jet1_corr,jet2_corr))
                jetmet1, jetmet2 = self.corrMET(jets_trk02[0], pdg1, jets_trk02[1], pdg2, event.met)
                self.tree.fill( 'Mj1j2_trk02_MetCorr',self.fillMass(jetmet1,jetmet2))
                #fillParticle(self.tree, 'Jet1_trk02_MetCorr', jetmet1)
                #fillParticle(self.tree, 'Jet2_trk02_MetCorr', jetmet2)

                jetmet1, jetmet2 = self.corrMET(jet1_corr, pdg1, jet2_corr, pdg2, event.met)
                self.tree.fill( 'Mj1j2_trk02_Corr_MetCorr',self.fillMass(jetmet1,jetmet2))
                fillParticle(self.tree, 'Jet1_trk02_Corr_MetCorr', jetmet1)
                fillParticle(self.tree, 'Jet2_trk02_Corr_MetCorr', jetmet2)

            if (len(jets_pf02)>1):  
                self.tree.fill( 'Mj1j2_pf02', self.fillMass(jets_pf02[0],jets_pf02[1]))
                jetmet1, jetmet2 = self.corrMET(jets_pf02[0], pdg1, jets_pf02[1], pdg2, event.met)
                self.tree.fill( 'Mj1j2_pf02_MetCorr', self.fillMass(jetmet1,jetmet2))

            if (len(jets_pf04)>1):  
                self.tree.fill( 'Mj1j2_pf04', self.fillMass(jets_pf04[0],jets_pf04[1]))
                jetmet1, jetmet2 = self.corrMET(jets_pf04[0], pdg1, jets_pf04[1], pdg2, event.met)
                self.tree.fill( 'Mj1j2_pf04_MetCorr', self.fillMass(jetmet1,jetmet2))

            if (len(jets_pf08)>1):  
                self.tree.fill( 'Mj1j2_pf08', self.fillMass(jets_pf08[0],jets_pf08[1]))
                jetmet1, jetmet2 = self.corrMET(jets_pf08[0], pdg1, jets_pf08[1], pdg2, event.met)
                self.tree.fill( 'Mj1j2_pf08_MetCorr', self.fillMass(jetmet1,jetmet2))





            if ( len(electrons) >=1 ): fillParticle(self.tree, 'Electron1', electrons[0])
            if ( len(electrons) >=2 ): fillParticle(self.tree, 'Electron2', electrons[1])

            if ( len(muons) >=1 ): fillParticle(self.tree, 'Muon1', muons[0])
            if ( len(muons) >=2 ): fillParticle(self.tree, 'Muon2', muons[1])

            ###################################
            #TMVA Stuff Starts!
            ###################################

            ###################################
            #qcd Background >>>>>>>>>>>>>>>>>
            ###################################
            
#            varlist = [
#                                "Jet1_tau32",
#                                "Jet2_tau32",
#                                "Jet1_tau21",
#                                "Jet2_tau21",
#                                "softDroppedJet1_m",
#                                "softDroppedJet2_m",
#                                "Jet1_trimmedProngMaxPtRatio",
#                                "Jet1_trimmedProngMinPtRatio",
#                                "Jet2_trimmedProngMaxPtRatio",
#                                "Jet2_trimmedProngMinPtRatio",
#            ]            
#            
#            inputs = ROOT.vector('string')()
#            for v in varlist:
#                inputs.push_back(v)
#
#            mva = ROOT.ReadQCD(inputs)
#            values = ROOT.vector('double')()
#        
#            values.push_back(Jet1_tau32)
#            values.push_back(Jet2_tau32)
#            values.push_back(Jet1_tau21)
#            values.push_back(Jet2_tau21)
#            values.push_back(jets[0].subjetsSoftDrop[0].m())
#            values.push_back(jets[1].subjetsSoftDrop[0].m())
#            values.push_back(Jet1_trimmedProngMaxPtRatio)
#            values.push_back(Jet1_trimmedProngMinPtRatio)
#            values.push_back(Jet2_trimmedProngMaxPtRatio)
#            values.push_back(Jet2_trimmedProngMinPtRatio)
#   
#            mva_value=mva.GetMvaValue(values)
#            self.tree.fill('BDTvariable_qcd', mva_value)
            
            ###################################
            #TMVA Stuff Ends!
            ###################################
            
            self.tree.tree.Fill()

    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()

