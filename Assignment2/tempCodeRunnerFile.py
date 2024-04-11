            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=False)
