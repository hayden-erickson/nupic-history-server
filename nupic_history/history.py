from nupic_history.sp_facade import SpFacade
from nupic_history.tm_facade import TmFacade
from nupic_history.io_client import FileIoClient

from nupic_history import SpSnapshots as SNAPS

class NupicHistory(object):


  def __init__(self, ioClient):
    """
    Provides top-level control over the SP History Facades.
    """
    self._ioClient = ioClient


  def createSpFacade(self, sp, save=None, modelId=None):
    """
    Creates a new active SP Facade for the given SP. Does not actually save
    anything yet.
    :param modelId: (string) pre-defined model id
    :param sp: SpatialPooler instance
    :param save: list of Snapshots to save with each compute step
    :return: [SpFacade] complete with a default redis client
    """
    return SpFacade(sp, self._ioClient, save=save, modelId=modelId)


  def getSpFacade(self, spId):
    """
    Get an inactive SP Facade by id, which can be used to playback the SP
    history.
    :param spId:
    :return: [SpFacade]
    """
    return SpFacade(spId, self._ioClient)


  def createTmFacade(self, tm, save=None, modelId=None):
    """
    Creates a new active TM Facade for the given TM. Does not actually save
    anything yet.
    :param modelId: (string) pre-defined model id
    :param tm: TemporalMemory instance
    :param save: list of Snapshots to save with each compute step
    :return: [SpFacade] complete with a default redis client
    """
    return TmFacade(tm, self._ioClient, save=save, modelId=modelId)


  def getTmFacade(self, tmId):
    """
    Get an inactive TM Facade by id, which can be used to playback the TM
    history.
    :param tmId:
    :return: [TmFacade]
    """
    return TmFacade(tmId, self._ioClient)


  def getColumnHistory(self, spId, columnIndex, states):
    out = {}
    for state in states:
      out[state] = []

    for iteration in xrange(self._ioClient.getMaxIteration(spId)):
      spFacade = SpFacade(spId, self._ioClient, iteration=iteration)
      spFacade.load()
      print spFacade._activeColumns
      for state in states:
        # Column activity only needs to be returned for the specified column.
        myState = spFacade.getState(state)[state]
        if state == SNAPS.ACT_COL:
          isActive = columnIndex in myState["indices"]
          if isActive:
            isActive = 1
          else:
            isActive = 0
          out[state].append(isActive)
        else:
          out[state].append(myState[columnIndex])

    return out


  def nuke(self):
    """
    Removes all traces of NuPIC History from Redis.
    :return:
    """
    self._ioClient.nuke(flush=True)
