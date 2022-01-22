import sys, re, random, time
nbr = []
letterWeights = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0,
    'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0,
    'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0}

#commonality rather tan dictionary, rather

def makeNbrTbl():
  for i in range(HEIGHT * WIDTH):
    cur = []
    cset = []
    for l in range(i + 1, (i // WIDTH) * WIDTH + WIDTH):
      cset.append(l)
    cur.append(cset)
    cset = []
    for r in range(i - 1, (i // WIDTH) * WIDTH - 1, -1):
      cset.append(r)
    cur.append(cset)
    cset = []
    for u in range(i - WIDTH, -1, -WIDTH):
      cset.append(u)
    cur.append(cset)
    cset = []
    for d in range(i + WIDTH, HEIGHT * WIDTH, WIDTH):
      cset.append(d)
    cur.append(cset)
    nbr.append(cur)

def dctLookUp(name, maxLen):
  allWords = set()
  lines = open(name, "r").read().splitlines()
  for l in lines:
    if 3 > len(l) or maxLen < len(l): continue
    allWords.add(l)
    permWord(l)
    wordFreq[len(l)][l] = {l}
  return allWords

def permWord(word):
  for ind in range(len(word)):
    letterWeights[word[ind]] += 1
    moreDotWord = (word[ind], ind)
    if moreDotWord not in wordFreq[len(word)]: wordFreq[len(word)][moreDotWord] = {word}
    else: wordFreq[len(word)][moreDotWord].add(word)

def wordScore(word, choiceScore):
  return choiceScore[word]

def makeCons(uFillPzl):
  cons = []
  for row in rows:
    curCons = []
    for r in row:
      if uFillPzl[r] == '#':
        if curCons: cons.append(tuple(curCons))
        curCons = []
      else:
        curCons.append(r)
    if curCons: cons.append(tuple(curCons))
  for col in cols:
    curCons = []
    for c in col:
      if uFillPzl[c] == '#':
        if curCons: cons.append(tuple(curCons))
        curCons = []
      else:
        curCons.append(c)
    if curCons: cons.append(tuple(curCons))

  adjCons = {con: [] for con in cons}
  for con in cons:
    for c in con:
      for con2 in cons:
        if c in con2 and con2 != con:
          adjCons[con].append(con2)

  avail = {con: set() for con in cons}
  for con in avail:
    cur = set()
    for key in wordFreq[len(con)]:
      cur = cur | wordFreq[len(con)][key]
    for ind, c in enumerate(con):
      p = uFillPzl[c]
      if p == '-': continue
      cur = cur & wordFreq[len(con)][(p, ind)]
    avail[con] = cur

  return avail, adjCons

def placeWords(pzl, availCons, used):
  printPzl(pzl)
  #printCons(availCons)
  if '-' not in pzl:
    return pzl if noRepWords(pzl) else ''
  nextCon, infos = choices2(pzl, availCons, used)
  if not nextCon: return ''
  for info in infos:
    np = info[0]
    newAvail = info[1]
    newUsed = info[2]
    c = info[3]
    if c in used: continue
    bF = placeWords(np, newAvail, newUsed)
    if bF:
      return bF
  return ''

def noRepWords(pzl):
  curWords = set()
  for con in availCons:
    curStr = ''
    for c in con:
      curStr += pzl[c]
    if curStr in curWords or curStr not in allWords: return False
    curWords.add(curStr)
  return True

def updateCons(pzl, availCons, curCon, choice, used):
  lPzl = [*pzl]
  for ind, pl in enumerate(curCon):
    if lPzl[pl] != '-': continue
    lPzl[pl] = choice[ind]
    #printPzl(lPzl)
    curNbrCon = nbrCons[curCon][ind]
    if not availCons[curNbrCon]: return False, lPzl
    if availCons[curNbrCon] == 'FILLED': continue
    for num, nbr in enumerate(curNbrCon):
      if nbr in curCon:
        if (choice[ind], num) not in wordFreq[len(curNbrCon)]: return False, ''.join(lPzl)
        newCon = availCons[curNbrCon] & wordFreq[len(curNbrCon)][(choice[ind], num)]
        break
    if not newCon:
      if not allLettersGood(lPzl, curNbrCon, used): return False, ''.join(lPzl)
    availCons[curNbrCon] = newCon
  availCons[curCon] = 'FILLED'
  used.add(choice)
  return True, ''.join(lPzl)



def allLettersGood(lPzl, curNbrCon, used):
  curWrd = ''
  for c in curNbrCon:
    if lPzl[c] == '-': return False
    curWrd += lPzl[c]
  return curWrd not in used

def choices2(pzl, availCons, used):
  bestChoices = [0] * 1000000
  bestCons = tuple()
  for cons in availCons:
    if availCons[cons] == 'FILLED': continue
    if not availCons[cons]:
      return '', ''
    if len(availCons[cons]) == 1:
      bestChoices = availCons[cons]
      bestCons = cons
      return bestCons, bestChoices
    if len(availCons[cons]) < len(bestChoices):
      bestChoices = availCons[cons]
      bestCons = cons

  infoList = []
  choiceScore = {}
  for c in bestChoices:
    tempCons = availCons.copy()
    newUsed = used.copy()
    yn, np = updateCons(pzl, tempCons, bestCons, c, newUsed)
    if not np: continue
    else:
      count = 0
      for key in nbrCons[bestCons]:
        count += len(tempCons[key])
      choiceScore[c] = count
    infoList.append((np, tempCons, newUsed, c))

  return bestCons, sorted(infoList, key=lambda r: wordScore(r[3], choiceScore), reverse=True)


def bruteForce(pzl, blkLeft):
  if isInvalid(pzl) or blkLeft < 0: return '' # check place at 20
  if not blkLeft: return pzl
  for i in choices(pzl):
    if pzl[i] != '-': continue
    lPzl = [*pzl]
    cur = blkLeft
    cur -= placeBlk(lPzl, i // WIDTH, i % WIDTH)
    np = ''.join(lPzl)
    if cur < 0 or np == pzl: continue
    printPzl(np)
    bF = bruteForce(np, cur)
    if bF: return bF
  return ''

def choices(pzl):
  unblkLines = [[] for x in range(50)]

  for ind, p in enumerate(pzl):
    if p == '#': continue
    count = 0
    for dir in nbr[ind]:
      if not dir: continue
      cc = 0
      for d in dir:
        if pzl[d] == '#':
          break
        cc += 1
      if cc < 3: break
      count += cc
    if cc >= 3: unblkLines[count].append(ind)

  order = []
  for x in range(len(unblkLines) - 1, 6, -1):
    if not unblkLines[x]: continue
    for ind in unblkLines[x]:
      order.append(ind)
  extra = order + [*range(length)]
  return extra

def isInvalid(pzl):
  if not check3HV(pzl): return True
  lPzl = [*pzl]
  notBlk = pzl.index('-')
  areaFill2(lPzl, notBlk // WIDTH, notBlk % WIDTH)
  return True if '-' in lPzl else False

def check3HV(pzl): # check that every non block character is in 2 words, at least 3 len
  for ind, p in enumerate(pzl):
    if p == '#': continue
    if not nbr[ind][0]: row = 1
    else:
      row = len(nbr[ind][0]) + 1
      for numLeft, lInd in enumerate(nbr[ind][0]):
        if pzl[lInd] == '#':
          row = numLeft + 1
          break

    if not nbr[ind][1]:
      row += 1
      if row < 3:
        return False
    else:
      row2 = len(nbr[ind][1])
      for numRight, rInd in enumerate(nbr[ind][1]):
        if pzl[rInd] == '#':
          row += numRight
          if row < 3:
            return False
      if row + row2 < 3:
        return False

    if not nbr[ind][2]:
      row = 1
    else:
      row = len(nbr[ind][2]) + 1
      for numLeft, uInd in enumerate(nbr[ind][2]):
        if pzl[uInd] == '#':
          row = numLeft + 1
          break

    if not nbr[ind][3]:
      row += 1
      if row < 3:
        return False
    else:
      row2 = len(nbr[ind][3])
      for numRight, dInd in enumerate(nbr[ind][3]):
        if pzl[dInd] == '#':
          row += numRight
          if row < 3:
            return False
      if row + row2 < 3:
        return False
  return True

def check180(pzl):
  for r in range(HEIGHT // 2 + 1):
    for c in range(WIDTH):
      cur = pzl[r * WIDTH + c]
      if cur != '#': continue
      if pzl[(HEIGHT - 1 - r) * WIDTH + (WIDTH - 1 - c)] != cur:
        return False
  return True

def areaFill2(lPzl, cr, cc):
  i = cr * WIDTH + cc
  if lPzl[i] == '#' or lPzl[i] == '+': return
  lPzl[i] = '+'
  if nbr[i][0]: areaFill2(lPzl, cr, cc + 1)
  if nbr[i][1]: areaFill2(lPzl, cr, cc - 1)
  if nbr[i][2]: areaFill2(lPzl, cr - 1, cc)
  if nbr[i][3]: areaFill2(lPzl, cr + 1, cc)

def placeBlk(lPzl, cr, cc):
  i = cr * WIDTH + cc
  oi = (HEIGHT - 1 - cr) * WIDTH + (WIDTH - 1 - cc)
  if lPzl[i] != '-' or lPzl[oi] != '-': return 0
  lPzl[i] = '#'
  lPzl[oi] = '#'
  placed = 0
  if i == oi:
    placed += 1
  else:
    placed += 2


  if nbr[i][0] and nbr[i][0][0] != '#':
    if len(nbr[i][0]) < 3:
      placed += placeBlk(lPzl, cr, cc + 1)
    else:
      cd = 0
      for l in nbr[i][0]:
        if cd >= 3: break
        if lPzl[l] == '#':
          placed += placeBlk(lPzl, cr, cc + 1)
        cd += 1

  if nbr[i][0] and nbr[i][0][0] != '#':
    if len(nbr[i][0]) < 3:
      placed += placeBlk(lPzl, cr, cc + 1)
    else:
      cd = 0
      for l in nbr[i][0]:
        if cd >= 3: break
        if lPzl[l] == '#':
          placed += placeBlk(lPzl, cr, cc + 1)
        cd += 1

  if nbr[i][1] and nbr[i][1][0] != '#':
    if len(nbr[i][1]) < 3:
      placed += placeBlk(lPzl, cr, cc - 1)
    else:
      cd = 0
      for l in nbr[i][1]:
        if cd >= 3: break
        if lPzl[l] == '#':
          placed += placeBlk(lPzl, cr, cc - 1)
        cd += 1

  if nbr[i][2] and nbr[i][2][0] != '#':
    if len(nbr[i][2]) < 3:
      placed += placeBlk(lPzl, cr - 1, cc)
    else:
      cd = 0
      for l in nbr[i][2]:
        if cd >= 3: break
        if lPzl[l] == '#':
          placed += placeBlk(lPzl, cr - 1, cc)
        cd += 1

  if nbr[i][3] and nbr[i][3][0] != '#':
    if len(nbr[i][3]) < 3:
      placed += placeBlk(lPzl, cr + 1, cc)
    else:
      cd = 0
      for l in nbr[i][3]:
        if cd >= 3: break
        if lPzl[l] == '#':
          placed += placeBlk(lPzl, cr + 1, cc)
        cd += 1
  return placed

def putSeeds(pzl, seeds, blkLeft):
  if not seeds: return pzl, blkLeft
  lPzl = [*pzl]
  for s in seeds:
    cs = re.search(r'^(\w)?(\d+)x(\d+)(.+)?$', s, re.I)
    cr = int(cs.group(2))
    cc = int(cs.group(3))
    i = cr * WIDTH + cc
    cseed = cs.group(4)
    hv = cs.group(1).lower()
    if not cseed or cseed == '#':
      blkLeft -= placeBlk(lPzl, cr, cc)
      continue
    if hv == 'h':
      nl = [i] + nbr[i][0]
      for ind in range(len(cseed)):
        if cseed[ind] == '#':
          blkLeft -= placeBlk(lPzl, nl[ind] // WIDTH, nl[ind] % WIDTH)
        else:
          lPzl[nl[ind]] = cseed[ind].lower()
    else:
      nl = [i] + nbr[i][3]
      for ind in range(len(cseed)):
        if cseed[ind] == '#':
          blkLeft -= placeBlk(lPzl, nl[ind] // WIDTH, nl[ind] % WIDTH)
        else:
          lPzl[nl[ind]] = cseed[ind].lower()
  filled = lPzl.copy()
  mInd = filled.index('-')
  areaFill2(filled, mInd // WIDTH, mInd % WIDTH)
  if not '-' in filled: return ''.join(lPzl), blkLeft
  one = filled.count('+')
  two = filled.count('-')
  if one < two:
    if one <= blkLeft:
      lPzl = ['#' if filled[x] == '+' else lPzl[x] for x in range(len(filled))]
      blkLeft -= one
    else:
      print('Impossible')
  else:
    if two <= blkLeft:
      lPzl = ['#' if filled[x] == '-' else lPzl[x] for x in range(len(filled))]
      blkLeft -= two
    else:
      print('Impossible')
  return ''.join(lPzl), blkLeft

def printPzl(pzl):
  for i in range(HEIGHT):
    for j in range(WIDTH):
      print(pzl[i * WIDTH + j], end='')
    print()
  print()

def printCons(availCons):
  for key in availCons:
    print(key, ':', availCons[key])

a = '5x5'
b = 0
c = 'dct20k.txt'
d = []
hw = re.search(r'^(\d*)x(\d*)$', a, re.I)
HEIGHT = int(hw.group(1))
WIDTH = int(hw.group(2))
blkLeft = int(b)
seedString = d
length = HEIGHT * WIDTH
'''hw = re.search(r'^(\d+)x(\d+)$', sys.argv[1], re.I)
HEIGHT = int(hw.group(1))
WIDTH = int(hw.group(2))
length = HEIGHT * WIDTH
blkLeft = int(sys.argv[2])
if length == blkLeft:
  printPzl('#' * length)
  exit(0)
seedString = sys.argv[4:]
'''
t = time.time()
maxLen = WIDTH if WIDTH > HEIGHT else HEIGHT
makeNbrTbl()
wordFreq = [{} for x in range(maxLen + 1)]
allWords = dctLookUp('/Users/maxgolub/Documents/PycharmProjects/Games/dct20k.txt', maxLen)
print('Time:', time.time() - t)
rows = [[*range(r * WIDTH, r * WIDTH + WIDTH)] for r in range(HEIGHT)]
cols = [[*range(c, length, WIDTH)] for c in range(WIDTH)]
pzl = '-' * (length)
pzl, blkLeft = putSeeds(pzl, seedString, blkLeft)
printPzl(pzl)
puzzleBlocks = bruteForce(pzl, blkLeft)
if puzzleBlocks:
  printPzl(puzzleBlocks)
else:
  print('Impossible')
availCons, nbrCons = makeCons(puzzleBlocks)
final = placeWords(puzzleBlocks, availCons, set())
printPzl(final)
print(time.time() - t)