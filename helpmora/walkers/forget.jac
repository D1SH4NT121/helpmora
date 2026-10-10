"""ForgetWalker — "Delete my data".

Deletes everything the chat wrote about this visitor under their own root:
the PersonNode, every NeedNode (and with it the scored eligible_for edges),
every ApplicationNode and every SessionInsight. The public program data
(ResourceNode, EligibilityRuleNode, FormNode) stays — it's the same for
everyone and holds nothing about the person. Deleting a node removes its
edges, so nothing personal is left reachable.

The client then drops the browser's anonymous login (a random id and
password with no personal data), so the next visit starts as a stranger.
"""

import from graph.nodes { PersonNode, NeedNode, ApplicationNode, SessionInsight }
import from graph.edges { has_need, applied_to, reflected_on }
import from engine.stats { reset_stats }

walker ForgetWalker {
    has user_id: str = "";
    has summary: dict = {};

    can forget with `Root entry {
        reset_stats();
        removed: dict = {"PersonNode": 0, "NeedNode": 0, "ApplicationNode": 0, "SessionInsight": 0};
        targets = [root --> [?:PersonNode, user_id == self.user_id]] if self.user_id else [root --> [?:PersonNode]];
        if not targets {
            targets = [root --> [?:PersonNode]];
        }
        for p in targets {
            for n in [p ->:has_need:-> [?:NeedNode]] {
                del n;
                removed["NeedNode"] += 1;
            }
            for a in [p ->:applied_to:-> [?:ApplicationNode]] {
                del a;
                removed["ApplicationNode"] += 1;
            }
            for s in [p ->:reflected_on:-> [?:SessionInsight]] {
                del s;
                removed["SessionInsight"] += 1;
            }
            del p;
            removed["PersonNode"] += 1;
        }
        self.summary = {"ok": True, "removed": removed};
        report self.summary;
    }
}

sem ForgetWalker is "Deletes the visitor's personal case data (PersonNode, NeedNodes, ApplicationNodes, SessionInsights) from their graph. Public program data is kept.";
