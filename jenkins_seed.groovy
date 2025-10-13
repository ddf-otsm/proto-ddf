import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.model.User
import jenkins.security.ApiTokenProperty

def j = Jenkins.instance

// Ensure job exists
def name = 'proto-ddf-local'
if (j.getItem(name) == null) {
  def job = j.createProject(WorkflowJob.class, name)
  def scm = new GitSCM('file:///Users/luismartins/local_repos/proto-ddf')
  def flow = new CpsScmFlowDefinition(scm, 'Jenkinsfile.local')
  flow.setLightweight(true)
  job.setDefinition(flow)
  job.save()
  println("✅ Created job: proto-ddf-local")
}

// Generate API token and save it
try {
  def user = User.get('admin', false)
  if (user != null) {
    def prop = user.getProperty(ApiTokenProperty.class)
    if (prop != null) {
      def tok = prop.getTokenStore().generateNewToken('local-cli-' + System.currentTimeMillis())
      new File(System.getenv('HOME') + '/vars/jenkins_api_token.txt').text = tok.plainValue
      user.save()
      println("✅ Generated API token: ~/vars/jenkins_api_token.txt")
    }
  }
} catch (Throwable t) {
  println("⚠️  Token generation failed: " + t.message)
}

// Trigger a build
try {
  def job = j.getItem(name)
  if (job != null) {
    job.scheduleBuild2(0)
    println("✅ Triggered build for proto-ddf-local")
  }
} catch (Throwable t) {
  println("⚠️  Build trigger failed: " + t.message)
}
