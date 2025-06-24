import PouchDB from 'pouchdb-browser'

const cache = {}

export function getDb(name) {
  if (!cache[name]) {
    cache[name] = new PouchDB(name)
  }
  return cache[name]
}

export function replicateDb(name, remoteUrl) {
  const db = getDb(name)
  const remote = new PouchDB(remoteUrl)
  db.sync(remote, { live: true, retry: true }).on('error', (err) => {
    // eslint-disable-next-line no-console
    console.error(`PouchDB sync error for ${name}:`, err)
  })
}
