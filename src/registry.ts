import { ServerConnection } from '@jupyterlab/services';

import { URLExt } from '@jupyterlab/coreutils';

import { IZenodoRegistry, ZenodoPost, ZenodoRecord } from './tokens';

export class ZenodoRegistry implements IZenodoRegistry {
  async updateDeposition(path: string) {
    const res = await ServerConnection.makeRequest(
      Private.getUrl('update', this._serverSettings),
      { method: 'POST' },
      this._serverSettings
    );

    const record = await Private.handleUpdateResponse(path, res);
    this._updateRecords(record);

    return record;
  }

  async createDeposition(path: string, post: ZenodoPost) {
    const res = await ServerConnection.makeRequest(
      Private.getUrl('upload', this._serverSettings),
      { method: 'POST', body: JSON.stringify(post) },
      this._serverSettings
    );

    const record = await Private.handleCreateResponse(path, res);
    this._updateRecords(record);

    return record;
  }

  async getDepositions() {
    if (!this._recordsFetched) {
      if (!this._recordsFetchPromise) {
        this._recordsFetchPromise = ServerConnection.makeRequest(
          Private.getUrl('status', this._serverSettings),
          { method: 'GET' },
          this._serverSettings
        ).then(Private.handleListResponse);
      }

      try {
        this._records = await this._recordsFetchPromise;
        this._recordsFetched = true;
      } catch (err) {
        throw err; // Re-raise
      } finally {
        delete this._recordsFetchPromise;
      }
    }

    return this._records;
  }

  hasDepositionSync(path: string) {
    return !!this._records.find(r => r.path === path);
  }

  private _serverSettings = ServerConnection.makeSettings();
  private _records = [] as ZenodoRecord[];
  private _recordsFetched = false;
  private _recordsFetchPromise: Promise<ZenodoRecord[]>;
  private _updateRecords = (record: ZenodoRecord): void => {
    const indexOf = this._records.findIndex(({ path }) => path === record.path);
    if (indexOf >= 0) {
      this._records = this._records
        .slice(0, indexOf)
        .concat([record], this._records.slice(indexOf + 1));
    } else {
      this._records = this._records.concat([record]);
    }
  };
}

namespace Private {
  export function getUrl(name: string, settings: ServerConnection.ISettings) {
    const parts = [settings.baseUrl, 'zenodo', name];
    return URLExt.join.apply(URLExt, parts);
  }

  export async function handleListResponse(
    res: Response
  ): Promise<ZenodoRecord[]> {
    const { records } = await res.json();
    console.log(records);
    if (!records || !Array.isArray(records)) {
      throw Error('Malformed response');
    }

    return records as ZenodoRecord[];
  }

  export async function handleUpdateResponse(
    path: string,
    res: Response
  ): Promise<ZenodoRecord> {
    if (res.status > 299) {
      const message = 'An error occurred updating the Zenodo deposition';
      throw new ServerConnection.ResponseError(res, message);
    }

    const json = await res.json();
    const doi = json.doi;

    if (!doi) {
      throw new Error('Missing DOI');
    }

    return { path, doi };
  }

  export async function handleCreateResponse(
    path: string,
    res: Response
  ): Promise<ZenodoRecord> {
    if (res.status > 299) {
      const message = 'An error occurred creating the Zenodo deposition';
      throw new ServerConnection.ResponseError(res, message);
    }

    const json = await res.json();

    const doi = json.doi;
    if (!doi) {
      throw new Error('Missing DOI');
    }

    const redirect = json.redirect;
    if (redirect) {
      window.open(redirect);
    }

    return { path, doi };
  }
}
