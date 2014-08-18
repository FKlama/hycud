from os import path

from FragValues       import FragValues
from Protein          import Protein
from CenterOfMass     import IndexedCoM
from HelperFunctions  import atomWeight


class FragStatistics:
  """Class for keeping the statistics for a fragment"""
  def __init__(self):
    self.n        = 0
    self.avg      = FragValues()
    self.stdDev   = FragValues()
    self.residues = 0


class Fragment:
  """Class describing fragments"""
  def __init__(self, num, modelPath):
    self.num          = num
    self.basename     = "Frag{:04n}".format(num)
    self.basepath     = path.join(modelPath, self.basename)
    self.values       = FragValues()
    self.protein      = Protein()
    self.center       = IndexedCoM()
    self.resCenters   = []
    self.stat         = FragStatistics()
    self.atomCount    = 0

  def calcValues(self, viscosity=0.0, HarmMe=0.0, radius=0.0):
    self.values.calcValues(viscosity=viscosity, HarmMe=HarmMe, radius=radius)

  def addAtom(self, atomName, resNum, resName, point):
    weight = atomWeight(atomName)
    self.center.addPoint(resNum, weight, point)
    self.protein.addResidue(resNum, resName)
    self.atomCount   += 1

  def getWeight(self):
    return self.protein.getWeight()

  def getProtons(self):
    return self.protein.getProtons()

  def getCenter(self):
    return self.center.getCenter()

  def getEta(self):
    return self.values.getEta()

  def getR(self, corr):
    return self.values.getR(corr)

  def getHM(self, corr):
    return self.values.getHM(corr)

  def getPDB(self):
    return self.basepath + '.pdb'

  def getDat(self):
    return self.basepath + '.dat'

  def doneParsing(self):  # This function simply exists to free memory
    self.protein.done()


class FragmentStatistics:
  def __init__(self, opt):
    self.stats              = []
    self.fragmentation      = opt.fragmentation
    for frag in self.fragmentation.fragments:
      stat = FragStatistics()
      stat.residues = frag.resCount()
      stat.resPrint = frag.resPrint()
      self.stats.append(stat)

  def populate(self, models):
    for m in models.models:
      for frag in m.fragments:
        self.stats[frag.num].avg.addTo(frag.values)
        self.stats[frag.num].n     += 1

    for s in self.stats:
      s.avg.divTo(s.n)

    for m in models.models:
      for frag in m.fragments:
        self.stats[frag.num].stdDev.addTo(frag.values.sub(self.stats[frag.num].avg).sqr())

    for s in self.stats:
      s.stdDev.divTo(s.n)
      s.stdDev.sqrtTo()
